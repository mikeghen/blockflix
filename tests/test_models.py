# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from blockflix.store.models import Staff, Country, City, Address, Actor, Category,\
                                Customer, Film, Language, Payment, \
                                Rental, Store, Role
from .factories import StaffFactory, CountryFactory, CityFactory, AddressFactory, \
                       ActorFactory, CategoryFactory, CustomerFactory, FilmFactory, \
                       LanguageFactory, PaymentFactory, RentalFactory, StoreFactory


@pytest.mark.usefixtures('db')
class TestStaff:
    """Staff tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = Staff('foo', 'foo@bar.com', first_name="Test", last_name="Test")
        user.save()

        retrieved = Staff.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        """Test creation date."""
        user = Staff(username='foo', email='foo@bar.com', first_name="Test", last_name="Test")
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        """Test null password."""
        user = Staff(username='foo', email='foo@bar.com', first_name="Test", last_name="Test")
        user.save()
        assert user.password is None

    def test_factory(self, db):
        """Test user factory."""
        user = StaffFactory(password='myprecious')
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password('myprecious')

    def test_check_password(self):
        """Check password."""
        user = Staff.create(username='foo', email='foo@bar.com',
                           password='foobarbaz123', first_name="Test", last_name="Test")
        assert user.check_password('foobarbaz123') is True
        assert user.check_password('barfoobaz') is False

    def test_full_name(self):
        """Staff full name."""
        user = StaffFactory(first_name='Foo', last_name='Bar')
        assert user.full_name == 'Foo Bar'

    def test_roles(self):
        """Add a role to a user."""
        role = Role(name='admin')
        role.save()
        user = StaffFactory()
        user.roles.append(role)
        user.save()
        assert role in user.roles

    def test_address(self):
        """Add a role to a user."""
        address = AddressFactory(address="123 Main St")
        address.save()
        user = StaffFactory()
        user.address = address
        user.save()
        assert address == user.address

    def test_relationships(self):
        store = StoreFactory()
        store.save()
        address = AddressFactory()
        address.save()
        staff = Staff(username='foo', email='foo@bar.com', first_name="Test", last_name="Test")
        staff.store = store
        staff.address = address
        staff.save()
        assert store == staff.store
        assert address == staff.address
        assert [staff] == store.staff
        assert [staff] == address.staff


@pytest.mark.usefixtures('db')
class TestCountry:
    """Country tests."""

    def test_get_by_id(self):
        """Get country by ID."""
        country = Country(country="USA")
        country.save()
        retrieved = Country.get_by_id(country.id)
        assert retrieved == country

    def test_factory(self, db):
        """Test country factory."""
        country = CountryFactory()
        db.session.commit()
        assert bool(country.country)


@pytest.mark.usefixtures('db')
class TestCity:
    """City tests."""

    def test_relationships(self):
        country = CountryFactory()
        country.save()
        city = City(city="New York")
        city.country = country
        city.save()
        assert country == city.country

    def test_factory(self, db):
        """Test country factory."""
        city = CityFactory()
        db.session.commit()
        assert bool(city.city)
        assert bool(city.country)


@pytest.mark.usefixtures('db')
class TestAddress:
    """Address tests."""

    def test_relationships(self):
        city = CityFactory()
        city.save()
        address = Address(address="123 Main St", postal_code="12345")
        address.city = city
        address.save()
        assert city == address.city

    def test_factory(self, db):
        """Test country factory."""
        address = AddressFactory()
        db.session.commit()
        assert bool(address.address)
        assert bool(address.city)
        assert bool(address.postal_code)


@pytest.mark.usefixtures('db')
class TestStore:
    """Store tests."""
    def test_relationships(self):
        staff = StaffFactory()
        staff.save()
        address = AddressFactory()
        address.save()
        store = Store()
        store.address = address
        store.manager = staff
        store.save()
        assert staff == store.manager
        assert address == store.address
        assert store in address.stores
        assert store in staff.managing_stores

    def test_factory(self, db):
        store = StoreFactory()
        db.session.commit()
        assert type(store.manager) == Staff
        assert type(store.address) == Address


@pytest.mark.usefixtures('db')
class TestLanguage:

    def test_relationships(self):
        language = Language(name="Test")
        language.save()
        film = FilmFactory(language=language)
        film.save()
        assert [film] == language.films

    def test_factory(self, db):
        language = LanguageFactory()
        db.session.commit()
        assert bool(language.name)



@pytest.mark.usefixtures('db')
class TestActor:

    def test_relationships(self):
        actor = Actor(first_name="Test", last_name="Test")
        actor.save()
        film = FilmFactory(actors=[actor])
        film.save()
        assert [film] == actor.films

    def test_factory(self, db):
        actor = ActorFactory()
        db.session.commit()
        assert bool(actor.first_name)
        assert bool(actor.last_name)


@pytest.mark.usefixtures('db')
class TestCategory:

    def test_relationships(self):
        category = Category(name="Test")
        category.save()
        film = FilmFactory(categories=[category])
        film.save()
        assert [film] == category.films

    def test_factory(self, db):
        category = CategoryFactory()
        db.session.commit()
        assert bool(category.name)


@pytest.mark.usefixtures('db')
class TestCustomer:
    """Customer tests."""

    def test_relationships(self):

        store = StoreFactory()
        store.save()
        address = AddressFactory()
        address.save()
        customer = Customer(first_name="Test", last_name="Test",
                            email="test@test.com", active=True)
        customer.address = address
        customer.store = store
        customer.save()
        assert store == customer.store
        assert address == customer.address
        assert customer in store.customers
        assert customer in address.customers

    def test_factory(self, db):
        customer = CustomerFactory()
        db.session.commit()
        assert type(customer.store) == Store
        assert type(customer.address) == Address


@pytest.mark.usefixtures('db')
class TestFilm:
    """Film tests."""

    def test_relationships(self):
        language = LanguageFactory()
        language.save()
        category = CategoryFactory()
        category.save()
        actor = ActorFactory()
        actor.save()
        film = Film(title="Test", description="Test",
                    release_year=2000, rental_duration=7, rental_rate=4.99,
                    replacement_cost=49.99, length=120)
        film.language = language
        film.categories = [category]
        film.actors = [actor]
        film.save()
        assert language == film.language
        assert category in film.categories
        assert actor in film.actors
        assert film in language.films
        assert film in category.films
        assert film in actor.films

    def test_factory(self, db):
        film = FilmFactory()
        db.session.commit()
        assert type(film.language) == Language


@pytest.mark.usefixtures('db')
class TestRental:

    def test_relationships(self):
        store = StoreFactory()
        store.save()
        staff = StaffFactory()
        staff.save()
        inventory = FilmFactory()
        inventory.save()
        store = StoreFactory()
        store.save()
        customer = CustomerFactory()
        customer.save()
        rental = Rental(inventory=inventory, customer=customer, staff=staff)
        rental.save()
        assert staff == rental.staff
        assert inventory == rental.inventory
        assert customer == rental.customer
        assert [rental] == staff.rentals
        assert [rental] == inventory.rentals
        assert [rental] == customer.rentals


    def test_factory(self, db):
        rental = RentalFactory()
        db.session.commit()
        assert type(rental.customer) == Customer
        assert type(rental.inventory) == Film
        assert type(rental.staff) == Staff


@pytest.mark.usefixtures('db')
class TestPayment:

    def test_relationships(self):
        staff = StaffFactory()
        staff.save()
        rental = RentalFactory()
        rental.save()
        customer = CustomerFactory()
        customer.save()
        payment = Payment(amount=5.99, customer=customer, rental=rental, staff=staff)
        assert staff == payment.staff
        assert rental == payment.rental
        assert customer == payment.customer
        assert [payment] == staff.payments
        assert [payment] == rental.payments
        assert [payment] == customer.payments


    def test_factory(self, db):
        payment = PaymentFactory()
        db.session.commit()
        assert type(payment.customer) == Customer
        assert type(payment.rental) == Rental
        assert type(payment.staff) == Staff
