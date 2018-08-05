# -*- coding: utf-8 -*-
"""Store controller."""
from flask import Blueprint, render_template, flash, redirect, request, url_for
from flask_login import login_required, current_user
from flask import jsonify
from blockflix.store.models import Film, Actor, Category, Payment


api_blueprint = Blueprint('api', __name__, url_prefix='/api', static_folder='../static')
film_blueprint = Blueprint('films', __name__, url_prefix='/films', static_folder='../static')
actor_blueprint = Blueprint('actors', __name__, url_prefix='/actors', static_folder='../static')
category_blueprint = Blueprint('categories', __name__, url_prefix='/categories', static_folder='../static')
payment_blueprint = Blueprint('payments', __name__, url_prefix='/payments', static_folder='../static')


@film_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def films():
    """List films."""
    if request.method == 'POST':
        films = Film.query.order_by(Film.popularity.desc()).limit(100).all()
        films = [film.to_dict() for film in films]
        return jsonify({'data': films})
    return render_template('films/index.html')

@payment_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def payments():
    """List payments."""
    if request.method == 'POST':
        print(current_user)
        payments = Payment.query.filter(Payment.user_id == current_user.get_id()).all()
        payments = [payment.to_dict() for payment in payments]
        return jsonify({'data': payments})
    return render_template('payments/index.html')

@actor_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def actors():
    """List actors."""
    if request.method == 'POST':
        actors = Actor.query.all()
        actors = [actor.to_dict() for actor in actors]
        return jsonify({'data': actors})
    return render_template('actors/index.html')


@category_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def categories():
    """List categories."""
    if request.method == 'POST':
        categories = Category.query.all()
        categories = [category.to_dict() for category in categories]
        return jsonify({'data': categories})
    return render_template('categories/index.html')
