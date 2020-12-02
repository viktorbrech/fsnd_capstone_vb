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

    # mini-frontend "Home", redirects to login page
    @app.route('/')
    def get_greeting():
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
    
    # @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    # @requires_auth(permission="delete:drinks")
    # def delete_drinks(payload, drink_id):
    #     drink = Drink.query.get(drink_id)
    #     if drink:
    #         drink.delete()
    #     else:
    #         abort(404)
    #     return jsonify({'success': True, 'delete': drink_id})

    # DELETE /movies/id

    # POST /actors
    @app.route('/actors', methods=['POST'])
    @requires_auth(permission="post:actors")
    def post_actors(payload):
        data = request.get_json()
        # TODO ensure proper type conversions inside the following constructor
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
        # TODO ensure proper type conversions inside the following constructor
        new_movie = Movie(
            title=data["title"],
            release_date=data["release_date"],
        new_movie.insert()
        return jsonify({'success': True, 'movies': [new_movie.format()]})

    # PATCH /actors/id

    # @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
    # @requires_auth(permission="patch:drinks")
    # def patch_drinks(payload, drink_id):
    #     data = request.get_json()
    #     drink = Drink.query.get(drink_id)
    #     if "title" in data:
    #         drink.title = data["title"]
    #     if "recipe" in data:
    #         if isinstance(data["recipe"], list):
    #             drink.recipe = json.dumps(data["recipe"])
    #         else:
    #             drink.recipe = json.dumps([data["recipe"]])
    #     drink.update()
    #     return jsonify({'success': True, 'drinks': [drink.long()]})
    
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