import os
import uuid
import pandas as pd
from ast import literal_eval
from tqdm import tqdm
from faker import Faker
from random import randint, uniform
from dateutil.relativedelta import relativedelta
from datetime import date
from numpy.random import choice
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import func
from blockflix.extensions import db
from blockflix.store.models import Category, Actor, Film, FilmCategory, FilmActor, \
                                Address, User, Payment, Rental


CURRENT = date(2017, 1, 1)
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','data')

def simulate():
    """
    Runs the seeding for Blockflix
    """
    clear_db()
    create_films()
    create_users_payments()
    create_rentals()


def clear_db():
    print("Resetting database...")
    FilmActor.query.delete()
    FilmCategory.query.delete()
    Category.query.delete()
    Actor.query.delete()
    Rental.query.delete()
    Film.query.delete()
    Payment.query.delete()
    Address.query.delete()
    User.query.delete()
    db.session.flush()
    db.session.commit()
    print("Database reset.")


def create_rentals():
    """
    Start from current date until today's date, increment by one month each time:
    - If a user has no rentals, rent a film
    - If a user has a rental, return the film based on a rental_probability
    """
    today = date.today()
    current = CURRENT
    session = db.session

    while current <= today:
        print("Building Rentals for {current}".format(current=current))
        users = User.query.filter(User.created_at <= current).all()
        for user in users:
            try:
                rental = Rental.query.filter(Rental.user == user, Rental.return_date == None).one()
                # Randomly decide whether to send the film back
                return_probability = 1 - 1 / ((current - rental.rental_date.date()).days/7)
                is_returned = choice([True, False], 1, p=[return_probability,1 - return_probability])
                if is_returned:
                    rental.return_date = current
                    rental.save()
            except NoResultFound:
                film = Film.query.filter(Film.release_date <= current, Film.popularity >= 5).order_by(func.rand()).first()
                rental = Rental(film=film, user=user,rental_date=current)
                rental.save()

        current += relativedelta(months=1)



def create_users_payments():
    """
    Start from current date until today's date:
    - Seed a base of n users and create payments for their first month
    - Grow the user base by a random rate 1 month at a time (e.g. 3% per month)
    - Create payments for all users each month, pays 9.99 on the first of the month
    """

    def user_info():
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = str(uuid.uuid4()).replace('-','')
        email = username + '@' + fake.free_email_domain()
        return { 'first_name': first_name,
                 'last_name': last_name,
                 'username': username,
                 'email': email,
                 'active': True }


    def address_info():
        return { 'address': fake.street_address(),
                 'district': fake.state(),
                 'postal_code': fake.zipcode(),
                 'city': fake.city(),
                 'phone': fake.phone_number() }


    fake = Faker('en')
    session = db.session

    today = date.today()
    current = CURRENT
    n = 100
    min_growth = 3
    max_growth = 5
    amount = 9.99

    # Build the first 100 users
    users = []
    users_count = 0
    print("Building first {0} users".format(n))
    for i in tqdm(range(0,n)):
        user = user_info()
        user['created_at'] = current
        users.append(user)
        users_count += 1
    users = [User(**user) for user in users]
    session.bulk_save_objects(users)
    users = User.query.with_entities(User.id).all()
    session.bulk_save_objects([
        Payment(user_id=user.id, payment_date=current, amount=9.99) for user in users
    ])
    session.commit()

    # Create users 1 month at a time until we reach today's date
    while current <= today:
        print("Building Users and Payments for {date}...".format(date=current.strftime("%Y-%m-%d")))
        year = current.year
        new_users_count = round(users_count * (uniform(min_growth,max_growth)/100))
        new_users = []
        for u in range(0, new_users_count):
            user = user_info()
            user['created_at'] = current
            new_users.append(user)
            users_count += 1
        new_users = [User(**user) for user in new_users]
        session.bulk_save_objects(new_users)

        # Add monthly payments for all users
        users = User.query.with_entities(User.id).all()
        session.bulk_save_objects([
            Payment(user_id=user.id, payment_date=current, amount=9.99) for user in users
        ])
        session.commit()

        print("BlockFlix now has {0} users".format(users_count))
        current += relativedelta(months=1)


    session.flush()
    session.commit()


def create_films():

    # Merge movies_metadata.csv with credits.csv, write to list of dicts
    films_df = pd.read_csv(os.path.join(DATA_PATH,'movies_metadata.csv'))
    credits_df = pd.read_csv(os.path.join(DATA_PATH,'credits.csv'))
    films_credits_df = pd.concat([films_df, credits_df], axis=1)

    films_credits_df["popularity"] = pd.to_numeric(films_credits_df["popularity"],errors='coerce')
    film_data = films_credits_df.dropna(subset=['cast','genres']).fillna(0).to_dict('records')



    # Linear scan over film_data and extract films, categories, and actors
    print("Parsing Films Data")
    films = {}
    categories = {}
    actors = {}
    film_actors = []
    film_categories = []

    # Process all the films, parse out the actors and the categories
    for row in tqdm(film_data):
        # Extract the film information
        film = {}
        film["id"] = row["id"]
        film["title"] = row["original_title"][0:45]
        film["description"] = row["overview"]
        if type(row["poster_path"]) == str and "jpg" in row["poster_path"]:
            film["poster_url"] = "https://image.tmdb.org/t/p/w185_and_h278_bestv2/" + row["poster_path"]
        if type(row["release_date"]) == str  and len(row["release_date"]) == 10:
            film["release_date"] = row["release_date"]
        try:
            film["popularity"] = float(row["popularity"])
        except (ValueError, TypeError) as e:
            film["popularity"] = 0
        try:
            film["length"] = int(float(row["runtime"]))
        except (ValueError, TypeError) as e:
            film["length"] = None
        # Add the film to the list of films, will save later
        films[film["id"]] = film

        # Extract the category information
        _categories = literal_eval(row["genres"])
        for category in _categories:
            category = {'id': category["id"], 'name': category["name"][0:25]}
            # Add the category and film_category relation to the list, will save later
            categories[category["id"]] = category
            film_categories.append((category["id"], film["id"]))

        # Extract the actor information
        _actors = literal_eval(row["cast"])
        for actor in _actors:
            name = actor["name"].split()
            actor["first_name"] = ' '.join(name[0:-1])
            actor["last_name"] = name[-1]
            actor = {'id': actor["id"], 'first_name': actor["first_name"], 'last_name': actor["last_name"]}
            # Add the actor and film_actor relation to the list, will save later
            actors[actor["id"]] = actor
            film_actors.append((actor["id"], film["id"]))

    print("Saving {0} categories, {1} actors, {2} films...".format(len(categories), len(actors), len(films)))
    db.session.add_all([
        Category(**category) for key, category in categories.items()
    ])
    db.session.add_all([
        Actor(**actor) for key, actor in actors.items()
    ])
    db.session.add_all([
        Film(**film) for key, film in films.items()
    ])
    # Flush before setting up relations
    db.session.flush()
    db.session.commit()
    db.session.add_all([
        FilmActor(actor_id=fa[0], film_id=fa[1]) for fa in film_actors
    ])
    db.session.add_all([
        FilmCategory(category_id=fc[0], film_id=fc[1]) for fc in film_categories
    ])
    db.session.flush()
    db.session.commit()
