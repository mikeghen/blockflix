
from csv import DictReader
from pprint import pprint
from json import loads
from ast import literal_eval
import pandas as pd
from sklearn import preprocessing
from progressbar import progressbar
from flask import current_app, Blueprint
from flask.cli import with_appcontext
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound
from blockflix.extensions import db
from blockflix.store.models import Category, Actor, Film, FilmCategory, FilmActor, \
                                Address, User, Payment, Rental
import os
import click
from faker import Faker
from random import randint, uniform
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, datetime
from hashlib import blake2s
from numpy.random import choice


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
user_index = 0
seed_blueprint = Blueprint('api', __name__, url_prefix='/seed', static_folder='../static')


def user_info():
    global user_index
    user_index += 1
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = fake.user_name() + str(user_index)
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


# @seed_blueprint.route('/user')
# def new_user():
#     """
#     Create a new user and payment.
#     """
#     user = user_info()
#     user = User(**user).save()
#     Payment(user_id=user.id, amount=12.99).save()
#     return 200
#
#
# @seed_blueprint.route('/rentals')
# def new_user():
#     """
#     Create a rental and return
#     """
#     # Rental
#     users = User.query.filter(User.rentals[0].return_date == None).order_by(func.rand()).first()
#     film = Film.query.order_by(func.rand()).first()
#     rental = Rental(film=film, user=user)
#     rental.save()
#
#     # Return
#     rental = Rental.query.filter(Rental.return_date == None).order_by(func.rand()).first()
#     rental.return_date = datetime.now()
#     rental.save()
#
#     return 200


@click.command()
@with_appcontext
def seed():
    seed_films_actors_categories()
    seed_addresses_users_payments()
    seed_rentals()


def seed_rentals():
    today = date.today()
    current = date(2010, 1, 1)
    session = db.session

    while current <= today:
        pprint("Week of {current}".format(current=current))
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
                    # print("RETURNED: {user}, {film}, {current}".format(user=user.username, film=rental.film.title, current=current))
                # else:
                #     print("RETAINED: {user}, {film}, {current}".format(user=user.username, film=rental.film.title, current=current))
            except NoResultFound:
                film = Film.query.filter(Film.release_date <= current, Film.popularity >= 5).order_by(func.rand()).first()
                rental = Rental(film=film, user=user,rental_date=current)
                rental.save()
                # print("RENTED: {user}, {film}, {current}".format(user=user.username, film=film.title, current=current))


        current += relativedelta(months=1)


def seed_addresses_users_payments():
    today = date.today()
    current = date(2010, 1, 1)
    fake = Faker('en')
    session = db.session

    Rental.query.delete()
    Payment.query.delete()
    Address.query.delete()
    User.query.delete()

    payments = []
    users = []
    users_count = 0
    print("Building first 100 users")
    for i in progressbar(range(0,100)):
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

    while current <= today:
        year = current.year
        if year < 2005:
            min_growth = 3
            max_growth = 5
            amount = 9.99
        elif year < 2010:
            min_growth = 5
            max_growth = 10
            amount = 10.99
        else:
            min_growth = 1
            max_growth = 3
            amount = 12.99
        print("Building Users and Payments for {date}...".format(date=current.strftime("%Y-%m-%d")))
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


def seed_films_actors_categories():
    """
    Create films, actors, and categories in the database according to the data
    from https://www.kaggle.com/rounakbanik/the-movies-dataset/data
    """
    # TODO: Languages

    # Merge movies_metadata.csv with credits.csv, write to list of dicts
    films_df = pd.read_csv(os.path.join(BASE_PATH,'data','movies_metadata.csv'))
    credits_df = pd.read_csv(os.path.join(BASE_PATH,'data','credits.csv'))
    films_credits_df = pd.concat([films_df, credits_df], axis=1)

    # Normailize the popularity
    films_credits_df["popularity"] = films_credits_df["popularity"].convert_objects(convert_numeric=True)
    film_data = films_credits_df.dropna(subset=['cast','genres']).fillna(0).to_dict('records')

    # Linear scan over film_data and extract films, categories, and actors
    print("Parsing Films Data")
    films = []
    film_ids = []
    categories = set()
    actors = set()
    actor_ids = set()
    film_actors = []
    film_categories = []

    #TODO: do this with Pandas
    for row in progressbar(film_data):
        # Extract film data
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
        except:
            film["popularity"] = 0

        try:
            film["length"] = int(float(row["runtime"]))
        except (ValueError, TypeError) as e:
            film["length"] = None

        # Extract the category information
        _categories = literal_eval(row["genres"])
        for category in _categories:
            category = (category["id"], category["name"][0:25])
            categories.add(category)
            film_categories.append((category[0], film["id"]))

        # Extract the actor information
        _actors = literal_eval(row["cast"])
        for actor in _actors:
            name = actor["name"].split()
            actor["first_name"] = ' '.join(name[0:-1])
            actor["last_name"] = name[-1]
            actor = (actor["id"], actor["first_name"], actor["last_name"])
            if actor[0] not in actor_ids:
                actors.add(actor)
                actor_ids.add(actor[0])
                film_actors.append((actor[0], film["id"]))

        if film["id"] not in film_ids:
            film_ids.append(film["id"])
            films.append(film)

    FilmActor.query.delete()
    FilmCategory.query.delete()
    Category.query.delete()
    Actor.query.delete()
    Film.query.delete()
    db.session.flush()
    db.session.commit()

    print("Saving categories, actors, films...")

    db.session.add_all([
        Category(id=category[0], name=category[1]) for category in categories
    ])
    db.session.add_all([
        Actor(id=actor[0], first_name=actor[1], last_name=actor[2]) for actor in actors
    ])
    db.session.add_all([
        Film(**film) for film in films
    ])
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
