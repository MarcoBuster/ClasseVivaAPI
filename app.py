import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_simple import (JWTManager, jwt_required, create_jwt, get_jwt_identity)
from datetime import datetime, timedelta
from src.classeviva.session import Session
from src.classeviva.errors import AuthenticationFailedError, NotLoggedInError

app = Flask(__name__)
app.secret_key = 'qwerty'
app.debug = True
app.threaded = True
CORS(app)
session = Session()
app.config['JWT_SECRET_KEY'] = 'somesecretkey'
app.config['JWT_EXPIRES'] = timedelta(minutes=30, hours=1)
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['credentials[username]']
    password = request.form['credentials[password]']
    session.login(username, password)
    ret = {'jwt': create_jwt(identity=username)}
    return jsonify(ret), 200


@app.route('/logout', methods=['DELETE'])
def logout():
    session.logout()
    return "Logged out"

@app.route('/grades')
@jwt_required
def get_grades():
    return session.grades()


@app.route('/absences')
@jwt_required
def get_absences():
    return session.absences()


@app.route('/didactics')
@jwt_required
def get_didactics():
    return session.didactics()


@app.route('/schoolbooks')
@jwt_required
def get_schoolbooks():
    return session.schoolbooks()


@app.route('/calendar')
@jwt_required
def get_calendar():
    return session.calendar()


@app.route('/cards')
@jwt_required
def get_cards():
    return session.cards()


@app.route('/lessons')
@jwt_required
def get_lessons():
    return session.lessons()


@app.route('/notes')
@jwt_required
def get_notes():
    return session.notes()


@app.route('/periods')
@jwt_required
def get_periods():
    return session.periods()

@app.route('/subjects')
@jwt_required
def get_subjects():
    return session.subjects()

@app.errorhandler(NotLoggedInError)
def not_logged_in(error):
    message = {
            'status': 403,
            'message': 'User not logged in',
    }
    resp = jsonify(message)
    resp.status_code = 403
    return resp

@app.errorhandler(AuthenticationFailedError)
def authentication_failed(error):
    message = {
            'status': 401,
            'message': 'Bad username or password',
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='localhost', port=port)
