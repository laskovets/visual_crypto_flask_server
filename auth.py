from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Experiments
from server import db
from lib.VisualCrypto import VisualCrypto
from lib.emailF import send_mail
import base64
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import quote
from lib.SGenerator import generate_password
from datetime import datetime
import cv2, hashlib

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST', 'GET'])
def login_post():
    email = request.form.get('email')

    user = User.query.filter_by(email=email).first()
    experiment = Experiments.query.filter_by(user_email=email, finished=False).first()
    attempt_counter = 10 - experiment.fail_counter
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database

    # if not user or not check_password_hash(user.password, password):
    if not user:
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    return render_template('login_shadow.html',
                           email=email,
                           shadow=quote(user.shadow.decode('ascii').rstrip('\n')),
                           attempt_counter=attempt_counter)


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST','GET'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    try:
        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    except:
        user = None

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    password, img = generate_password()

    vc = VisualCrypto(2)
    vc.image=img
    vc.processImage()
    vc.makeBaseMatrix()
    vc.splitImage()
    res_to_db = vc.shadows[0]
    res_to_email = vc.shadows[1]

    _, buffer = cv2.imencode('.png', res_to_db)
    byteArr = base64.b64encode(buffer)

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), shadow=byteArr)
    new_user.shadows_generating_count += 1
    new_experiments = Experiments(user_email=email, original_password=password)

    _, buffer = cv2.imencode('.png', res_to_email)
    imgObj = buffer.tobytes()

    send_mail('a.laskovets@gmail.com', [email], 'Generated shadow', 'Generate text for authentication', [imgObj])

    # add the new user to the database
    db.session.add(new_user)
    db.session.add(new_experiments)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    email = current_user.email
    logout_user()
    password, img = generate_password()

    vc = VisualCrypto(2)
    vc.image = img
    vc.processImage()
    vc.makeBaseMatrix()
    vc.splitImage()
    res_to_db = vc.shadows[0]
    res_to_email = vc.shadows[1]

    _, buffer = cv2.imencode('.png', res_to_db)
    byteArr = base64.b64encode(buffer)
    print("shadow hash {}".format(hashlib.md5(byteArr).digest()))

    user = User.query.filter_by(email=email).first()
    user.experiments_count += 1
    user.shadows_generating_count += 1
    # create new user with the form data. Hash the password so plaintext version isn't saved.

    user.password = generate_password_hash(password, method='sha256')
    user.shadow = byteArr
    new_experiments = Experiments(user_email=email, original_password=password)

    _, buffer = cv2.imencode('.png', res_to_email)
    imgObj = buffer.tobytes()

    db.session.add(new_experiments)
    db.session.commit()

    send_mail('a.laskovets@gmail.com', [email], 'Generated shadow', 'Generate text for authentication', [imgObj])
    return render_template('login.html')


@auth.route('/login_shadow', methods=['POST', 'GET'])
def login_shadow_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    experiment = Experiments.query.filter_by(user_email=email, finished=False).first()
    current_time = datetime.utcnow().timestamp()
    exp_time = experiment.creation_date.timestamp()
    duration = current_time - exp_time
    experiment.duration = duration

    if duration >= 600:
        experiment.finished = True
        db.session.commit()
        return recreate_password_for_user(email)

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        experiment.fail_counter += 1
        if experiment.failed_passwords is None:
            experiment.failed_passwords = ''
        experiment.failed_passwords += password + ';'
        print(experiment.fail_counter)
        if experiment.fail_counter == 10:
            experiment.finished = True
            db.session.commit()
            return recreate_password_for_user(email)
        db.session.commit()
        flash('Please check your login details and try again.')
        experiment = Experiments.query.filter_by(user_email=email, finished=False).first()
        attempt_counter = 10 - experiment.fail_counter
        return render_template('login_shadow.html',
                               email=email,
                               shadow=quote(user.shadow.decode('ascii').rstrip('\n')),
                               attempt_counter=attempt_counter)
    experiment.successful = True
    experiment.finished = True
    db.session.commit()
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


def recreate_password_for_user(email):
    password, img = generate_password()

    vc = VisualCrypto(2)
    vc.image = img
    vc.processImage()
    vc.makeBaseMatrix()
    vc.splitImage()
    res_to_db = vc.shadows[0]
    res_to_email = vc.shadows[1]

    _, buffer = cv2.imencode('.png', res_to_db)
    byteArr = base64.b64encode(buffer)

    user = User.query.filter_by(email=email).first()
    user.experiments_count += 1
    user.shadows_generating_count += 1
    new_experiments = Experiments(user_email=email, original_password=password)
    # create new user with the form data. Hash the password so plaintext version isn't saved.

    user.password = generate_password_hash(password, method='sha256')
    user.shadow = byteArr

    _, buffer = cv2.imencode('.png', res_to_email)
    imgObj = buffer.tobytes()

    db.session.add(new_experiments)
    db.session.add(user)
    db.session.commit()

    send_mail('a.laskovets@gmail.com', [email], 'Generated shadow', 'Generate text for authentication', [imgObj])
    return redirect(url_for('auth.login'))
