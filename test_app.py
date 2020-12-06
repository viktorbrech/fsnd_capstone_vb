import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie, db_drop_and_create_all
from auth import AuthError, requires_auth

# reset the database
db_drop_and_create_all()
print("db reset")


#----------------------------------------------------------------------------#
# JWTs for every role.
#----------------------------------------------------------------------------#

EXECUTIVE_PRODUCER_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTcyNDg3MjI1OTI2MjExNDg0NzkiLCJhdWQiOlsiY2Fwc3RvbmVfYXBpIiwiaHR0cHM6Ly92YnJlY2guZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwNzI0OTY0MCwiZXhwIjoxNjA3MzM2MDQwLCJhenAiOiJNWkYwQlY3NjY2UE1JN2NzZHF0eG9BN3Z1THJxUDYwRiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOm1vdmllcyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiLCJwb3N0Om1vdmllcyJdfQ.osFHmMRmH84UT2wkVU1gy-Qlq8r6v2x2pMDO5aLujwuS82_WjfHGAMznB5bCVsyGDI-iLwyQT-FN2oT0kxI289NOXcZAbqSxCED7ppOw7sIaVQAbM_t6XgbsSKFMGKjJgtzo8tbfL1IjpBzvdro6Ti-3Df838dRDnQFiDy3ECT_gcxaqW1-dcFtLKWesVcucm9UEObdmvc3sqv537ynsf_4Aro6fVR5U5EICWn3uFevXxiLHmVVLGoWXAtxIhJ-gUlSSfNVtmoEuXT7mElvgaDYWy1P_uvSEICWP65nOyvVXQqTJj1rDd3zj6g4XXIl7YpHNPsvGbQw2Asz810XafQ"


#----------------------------------------------------------------------------#
# Test class
#----------------------------------------------------------------------------#


class AgencyTestCase(unittest.TestCase):
    """This class represents the casting agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        #self.database_name = "trivia_test"
        self.database_path = os.environ['DATABASE_URL']
        setup_db(self.app, self.database_path)

        self.new_actor = {
            "name": "Jack Johnson",
            "age": 30,
            "gender": "male"
        }

        self.incomplete_actor = {
            "age": 33,
            "gender": "female"
        }

        self.new_movie = {
            "title": "Supercop",
            "release_date": "1994-12-24"
        }

        self.incomplete_movie = {
            "release_date": "1998-12-25"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    #----------------------------------------------------------------------------#
    # Test every endpoint.
    #----------------------------------------------------------------------------#

    # def test_success_get_questions_page(self):
    #     res = self.client().get('/questions?page=1')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['total_questions'] > 0)
    #     self.assertTrue(data['questions'])
    #     self.assertTrue(data['categories'])

    # def test_404_beyond_range(self):
    #     res = self.client().get('/questions?page=1000')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'resource not found')

    # def test_success_create_question(self):
    #     res = self.client().post('/questions', json=self.new_question)
    #     data = json.loads(res.data)
    #     question = Question.query.filter(Question.answer == "Kingsley Amis").one_or_none()
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertFalse(question == None)
    

    # tests for the "GET /actors" endpoint
    def test_a_a_success_get_actors(self):
        res = self.client().get(
            '/actors',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "GET /movies" endpoint
    def test_b_a_success_get_movies(self):
        res = self.client().get(
            '/movies',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "POST /actors" endpoint
    def test_c_a_success_create_actor(self):
        res = self.client().post(
            '/actors',
            json=self.new_actor,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "POST /movies" endpoint
    def test_d_a_success_create_movie(self):
        res = self.client().post(
            '/movies',
            json=self.new_movie,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "PATCH /actors/id" endpoint
    def test_e_a_success_update_actor(self):
        res = self.client().patch(
            '/actors/1',
            json=self.incomplete_actor,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "PATCH /movies/id" endpoint
    def test_f_a_success_update_movie(self):
        res = self.client().patch(
            '/movies/1',
            json=self.incomplete_movie,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "DELETE /actors/id" endpoint
    def test_g_a_success_delete_actor(self):
        res = self.client().delete(
            '/actors/1',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # tests for the "DELETE /movies/id" endpoint
    def test_h_a_success_delete_movie(self):
        res = self.client().delete(
            '/movies/1',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    #----------------------------------------------------------------------------#
    # RBAC tests for the Casting Assistant
    #----------------------------------------------------------------------------#

    # SHOULD access get:actors endpoint

    # should NOT access post:actors endpoint

    #----------------------------------------------------------------------------#
    # RBAC tests for the Casting Director
    #---------------------------------------------------------------------------#

    # SHOULD access patch:actors endpoint

    # should NOT access post:movies endpoint


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()