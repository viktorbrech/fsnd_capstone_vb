import os
from flask import (
    Flask,
    request,
    jsonify,
    abort,
    render_template,
    redirect,
    url_for
)
from sqlalchemy import exc
import json
from flask_cors import CORS
from datetime import date
import time

from models import setup_db, Actor, Movie, db_drop_and_create_all
from auth import AuthError, requires_auth

# uncomment the following line to reset the database upon flask run
# db_drop_and_create_all()


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # mini-frontend "Home" page, redirects to login page
    @app.route('/')
    def home_page():
        return redirect(url_for('login_page'))

    # mini-frontend "Login" page
    @app.route('/login')
    def login_page():
        return render_template("login.html")

    # mini-frontend "Callback" page, Auth0 redirects to here with access_token
    @app.route('/callback')
    def callback_page():
        return render_template("callback.html")

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
    @app.route('/movies')
    @requires_auth(permission="get:movies")
    def get_movies(payload):
        all_movies = Movie.query.all()
        movies = []
        for movie in all_movies:
            movies.append(movie.format())
        return jsonify({"success": True, "movies": movies})

    # DELETE /actors/id
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth(permission="delete:actors")
    def delete_actors(payload, actor_id):
        actor = Actor.query.get(actor_id)
        if actor:
            actor.delete()
        else:
            abort(404)
        return jsonify({'success': True, 'delete': actor_id})

    # DELETE /movies/id
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth(permission="delete:movies")
    def delete_movies(payload, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.delete()
        else:
            abort(404)
        return jsonify({'success': True, 'delete': movie_id})

    # POST /actors
    @app.route('/actors', methods=['POST'])
    @requires_auth(permission="post:actors")
    def post_actors(payload):
        data = request.get_json()
        new_actor = Actor(
            name=data["name"],
            age=data["age"],
            gender=data["gender"])
        new_actor.insert()
        return jsonify({'success': True, 'actors': [new_actor.format()]})

    # POST /movies
    @app.route('/movies', methods=['POST'])
    @requires_auth(permission="post:movies")
    def post_movies(payload):
        data = request.get_json()
        try:
            assert "title" in data
            release_date = date.fromisoformat(data["release_date"])
        except:
            abort(422)
        new_movie = Movie(
            title=data["title"],
            release_date=release_date)
        new_movie.insert()
        return jsonify({'success': True, 'movies': [new_movie.format()]})

    # PATCH /actors/id
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth(permission="patch:actors")
    def patch_actors(payload, actor_id):
        data = request.get_json()
        actor = Actor.query.get(actor_id)
        if not actor:
            abort(404)
        if "name" in data:
            actor.name = data["name"]
        if "age" in data:
            actor.age = data["age"]
        if "gender" in data:
            actor.gender = data["gender"]
        actor.update()
        return jsonify({'success': True, 'actors': [actor.format()]})
    
    # PATCH /movies/id
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth(permission="patch:movies")
    def patch_movies(payload, movie_id):
        data = request.get_json()
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404)
        if "title" in data:
            movie.title = data["title"]
        if "release_date" in data:
            try:
                release_date = date.fromisoformat(data["release_date"])
            except:
                abort(422)
            movie.release_date = release_date
        movie.update()
        return jsonify({'success': True, 'movies': [movie.format()]})

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