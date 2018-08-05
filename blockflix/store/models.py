# -*- coding: utf-8 -*-
"""
Blockflix Store models.
"""
import datetime as dt
from flask_login import UserMixin
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from blockflix.database import Column, Model, SurrogatePK, db, reference_col, relationship
from blockflix.extensions import bcrypt

"""
Association Tables: Tables used for many-to-many relationships, no need to
                    create classes since these won't be referenced in ORM layer
"""

films_actors = db.Table('films_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id'), nullable=False),
    db.Column('film_id', db.Integer, db.ForeignKey('films.id'), nullable=False)
)

films_categories = db.Table('films_categories',
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), nullable=False),
    db.Column('film_id', db.Integer, db.ForeignKey('films.id'), nullable=False)
)

class FilmCategory(SurrogatePK, Model):
    __tablename__ = 'films_categories'
    category_id = Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    film_id = Column(db.Integer, db.ForeignKey('films.id'), nullable=False)


class FilmActor(SurrogatePK, Model):
    __tablename__ = 'films_actors'
    actor_id = Column(db.Integer, db.ForeignKey('actors.id'), nullable=False)
    film_id = Column(db.Integer, db.ForeignKey('films.id'), nullable=False)


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):

    __tablename__ = 'users'
    first_name = Column(db.String(45), nullable=False)
    last_name = Column(db.String(45), nullable=False)
    picture = Column(mysql.BLOB())
    email = Column(db.String(50))
    active = Column(db.Boolean())
    username = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.Binary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if not self.created_at:
            self.created_at = dt.datetime.utcnow()
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)


class Actor(SurrogatePK, Model):
    __tablename__ = 'actors'
    first_name = Column(db.String(45), nullable=False)
    last_name = Column(db.String(45), nullable=False)
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    films = db.relationship('Film', secondary=films_actors)

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Actor ({full_name})>'.format(full_name=self.full_name)

    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name
        }


class Address(SurrogatePK, Model):
    __tablename__ = 'addresses'
    address = Column(db.String(50), nullable=False)
    address2 = Column(db.String(50), default=None)
    district = Column(db.String(20))
    city = Column(db.String(50))
    postal_code = Column(db.String(10), nullable=False, default=None)
    phone = Column(db.String(20), nullable=True)
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())


    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Address ({address})>'.format(address=self.address)


class Category(SurrogatePK, Model):
    __tablename__ = 'categories'
    name = Column(db.String(25), nullable=False)
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    films = db.relationship('Film', secondary=films_categories)


    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Category ({name})>'.format(name=self.name)

    def to_dict(self):
        return {
            'name': self.name
        }



class Film(SurrogatePK, Model):
    __tablename__ = 'films'
    title = Column(db.String(45), nullable=False)
    description = Column(mysql.TEXT(), nullable=False)
    poster_url = Column(db.String(500))
    release_date = Column(db.Date)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    original_language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    popularity = Column(db.Float())
    length = Column(db.Integer())
    replacement_cost =  Column(db.Float())
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    language = db.relationship('Language', foreign_keys=[language_id], backref='films', lazy=True)
    actors = db.relationship('Actor', secondary=films_actors)
    categories = db.relationship('Category', secondary=films_categories)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Film ({title})>'.format(title=self.title)

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'release_date': self.release_date.strftime('%Y-%m-%d') if self.release_date else '',
            'length': self.length,
            'popularity': self.popularity
        }


class Language(SurrogatePK, Model):
    __tablename__ = 'languages'
    name = Column(db.String(45), nullable=False)
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())


class Payment(SurrogatePK, Model):
    __tablename__ = 'payments'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = Column(db.Float(), nullable=False)
    payment_date = Column(db.DateTime, nullable=False, server_default=func.now())
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    user = db.relationship('User', foreign_keys=[user_id], backref='payments', lazy=True)

    def to_dict(self):
        return {
            'amount': self.amount,
            'payment_date': self.payment_date.strftime('%Y-%m-%d') if self.payment_date else '',
            'user': self.user.full_name
        }


class Rental(SurrogatePK, Model):
    __tablename__ = 'rentals'
    rental_date = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    return_date = Column(db.DateTime)
    last_update = Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    film = db.relationship('Film', foreign_keys=[film_id], backref='rentals', lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], backref='rentals', lazy=True)
