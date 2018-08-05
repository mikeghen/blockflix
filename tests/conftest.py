# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from webtest import TestApp
from blockflix.app import create_app
from blockflix.database import db as _db
from blockflix.settings import TestConfig

from .factories import StaffFactory


@pytest.fixture
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.execute("DROP DATABASE blockflix_test")
    _db.session.execute("CREATE DATABASE blockflix_test")
    _db.session.close()
    #
    # _db.drop_all()




@pytest.fixture
def user(db):
    """A user for the tests."""
    user = StaffFactory(password='myprecious')
    db.session.commit()
    return user
