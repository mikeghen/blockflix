# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from blockflix.database import db
from blockflix.store.models import Staff, Country, City, Address, Actor, Category,\
                                Customer, Film, Language, Payment, \
                                Rental, Store


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class StaffFactory(BaseFactory):
    """Staff factory."""

    username = Sequence(lambda n: 'user{0}'.format(n))
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    first_name = Sequence(lambda n: 'Test{0}'.format(n))
    last_name = Sequence(lambda n: 'Test{0}'.format(n))
    active = True

    class Meta:
        model = Staff


class CountryFactory(BaseFactory):
    class Meta(object):
        model = Country

    country = Sequence(lambda n: 'country{0}'.format(n))


class CityFactory(BaseFactory):
    class Meta:
        model = City

    city = Sequence(lambda n: 'city{0}'.format(n))
    country = SubFactory(CountryFactory)


class AddressFactory(BaseFactory):
    class Meta:
        model = Address

    address = Sequence(lambda n: '{0} main st'.format(n))
    postal_code = Sequence(lambda n: '{0}'.format(n))
    city = SubFactory(CityFactory)


class StoreFactory(BaseFactory):
    class Meta:
        model = Store

    manager = SubFactory(StaffFactory)
    address = SubFactory(AddressFactory)


class LanguageFactory(BaseFactory):
    class Meta:
        model = Language

    name = Sequence(lambda n: 'Language{0}'.format(n))


class ActorFactory(BaseFactory):
    class Meta:
        model = Actor

    first_name = Sequence(lambda n: 'Actor{0}'.format(n))
    last_name = Sequence(lambda n: 'Actor{0}'.format(n))


class CategoryFactory(BaseFactory):
    class Meta:
        model = Category

    name = Sequence(lambda n: 'Category{0}'.format(n))


class CustomerFactory(BaseFactory):
    class Meta:
        model = Customer

    first_name = Sequence(lambda n: 'Customer{0}'.format(n))
    last_name = Sequence(lambda n: 'Customer{0}'.format(n))
    email = Sequence(lambda n: 'customer{0}@example.com'.format(n))
    active = True
    store = SubFactory(StoreFactory)
    address = SubFactory(AddressFactory)


class FilmFactory(BaseFactory):
    class Meta:
        model = Film

    title = Sequence(lambda n: 'Film{0}'.format(n))
    description = "This is a film"
    release_year = Sequence(lambda n: 2000 + n)
    rental_duration = 7
    rental_rate = 5.99
    length = 120
    replacement_cost = 49.99
    language = SubFactory(LanguageFactory)


class RentalFactory(BaseFactory):
    class Meta:
        model = Rental

    film = SubFactory(FilmFactory)
    staff = SubFactory(StaffFactory)
    customer = SubFactory(CustomerFactory)


class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    amount = 5.99
    customer = SubFactory(CustomerFactory)
    staff = SubFactory(StaffFactory)
    rental = SubFactory(RentalFactory)
