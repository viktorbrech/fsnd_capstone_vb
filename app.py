import os
from flask import Flask
from models import setup_db
from flask_cors import CORS

from auth import AuthError, requires_auth

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

    @app.route('/coolkids')
    def be_cool():
        return "Be cool, man, be coooool! You're almost a FSND grad!"

    # GET /actors
    @app.route('/actors')
    @requires_auth(permission="get:actors")
    def get_actors(payload):
        all_actors = Actor.query.all()
        actors = []
        for actor in all_actors:
            actors.append(actor.format())
        return jsonify({"success": True, "actors": actors})

    # GET /movies
    @app.route('/movie')
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

    return app

app = create_app()

if __name__ == '__main__':
    app.run()