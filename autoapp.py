# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from blockflix.app import create_app
from blockflix.database import db
from blockflix.settings import DevConfig, ProdConfig


CONFIG = DevConfig if get_debug_flag() else ProdConfig

application = create_app(CONFIG)
