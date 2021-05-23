from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Experiments
from server import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    rows = Experiments.query.all()
    return render_template('index.html', rows=rows)


@main.route('/profile')
@login_required
def profile():
    email = current_user.email
    rows = Experiments.query.filter_by(user_email=email)
    return render_template('profile.html', name=current_user.name, rows=rows)

