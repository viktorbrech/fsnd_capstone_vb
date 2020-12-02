import os
from flask import Flask, request, jsonify, abort, render_template
from sqlalchemy import exc
import json
from flask_cors import CORS

from models import setup_db, Actor, Movie
from auth import AuthError, requires_auth

import http.client

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def get_greeting():
        excited = os.environ['EXCITED']
        greeting = "Hello" 
        if excited == 'true': greeting = greeting + "!!!!!"
        return greeting

    @app.route('/login')
    def login_page():
        return render_template("login.html")

    @app.route('/callback')
    def callback_page():

conn = http.client.HTTPSConnection("")
payload = "grant_type=authorization_code&client_id=%24%7Baccount.clientId%7D&client_secret=YOUR_CLIENT_SECRET&code=YOUR_AUTHORIZATION_CODE&redirect_uri=%24%7Baccount.callback%7D"
headers = { 'content-type': "application/x-www-form-urlencoded" }
conn.request("POST", "/vbrech.eu.auth0.com/oauth/token", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
        return render_template("callback.html")

    @app.route('/coolkids')
    def be_cool():
        return "Be cool, man, be coooool! You're almost a FSND grad!"

    # GET /actors
    @app.route('/actors')
    # @requires_auth(permission="get:actors")
    def get_actors():
        all_actors = Actor.query.all()
        actors = []
        for actor in all_actors:
            actors.append(actor.format())
        return jsonify({"success": True, "actors": actors})

    # GET /movies
    @app.route('/movies')
    @requires_auth(permission="get:movies")
    def get_movies(payload):
        all_movies = Movie.query.all()
        movies = []
        for movie in all_movies:
            movies.append(movie.format())
        return jsonify({"success": True, "movies": movies})

    # DELETE /actors/id

    # DELETE /movies/id

    # POST /actors

    # POST /movies

    # PATCH /actors/id

    # PATCH /movies/id

    """
    ERROR HANDLERS TAKEN FROM MY COFFEE_SHOP PROJECT SUBMISSION
    """
    # Error Handling
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False,
                        "error": 422,
                        "message": "unprocessable"
                        }), 422


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
                        "success": False,
                        "error": 400,
                        "message": "unprocessable"
                        }), 400


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404


    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
                        "success": False,
                        "error": error.status_code,
                        "message": error.error
                        }), error.status_code
    return app

app = create_app()

if __name__ == '__main__':
    app.run()