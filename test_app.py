import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie, db_drop_and_create_all
from auth import AuthError, requires_auth


# ---------------------------------------------------------------------------#
# JWTs for every role.
# ---------------------------------------------------------------------------#

EXECUTIVE_PRODUCER_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWZjZmQxNDE5YWJkNzAwMDZlNDE5ZWY3IiwiYXVkIjoiY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjA3NDYwMjkyLCJleHAiOjE2MDc1NDY2OTIsImF6cCI6Ik1aRjBCVjc2NjZQTUk3Y3NkcXR4b0E3dnVMcnFQNjBGIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOm1vdmllcyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiLCJwb3N0Om1vdmllcyJdfQ.yDYLdsckNW2EwK4_jse6Y1ZLbUviX_lCmbfBYvdDw4yD4c6rkGvb-r-EcCfR55KzM46qETHho8hsZY8sLpV_gikkyz20hVntBUMRc_bZycTf0q8E-MRVM8-dsplXyTa-9yutwlYaAmVxCAoI4OyoyEOhBTCthKVzd2xp55OPM5sMJlIXGZSwABEvfrSJ-m0wxfRTIMUfHaDxqtwYe8l2zDCRTLD_vZeSSG7COy1MAE7MjdXIynTyCRFqZRz0jcD9FS-YXaQZ8Gqj3u8XiJWjgBtOz7X7pc1FyW65u-T2PD2ZeTK1l_WdyPBJGLTWVJSHkwg50FsbenGW2W5tOp9XOg"
CASTING_ASSISTANT_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWZjZmQwOTM1ZWRmMjgwMDY4NDVmOWYwIiwiYXVkIjoiY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjA3NDYwMTk2LCJleHAiOjE2MDc1NDY1OTYsImF6cCI6Ik1aRjBCVjc2NjZQTUk3Y3NkcXR4b0E3dnVMcnFQNjBGIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyJdfQ.dqaq9wewAk_I-yMB-k8XbFv8ixCd-khXs_fvNERLwMT9e2GtXrfZZ-OZsqSRR_XSl0iO5THVo464hvqiBqiTMkFwTN82UHjwtnj1FoHV9rM-oFXXIdwJKjZZGk21K9HTou-ah5ne7gqwCP0y-q-GGdwqe3MVdh1iuFofbBa_9TpksgChYaYayXTzFOv_6imnnuj247V95mwlF1c0gLu5sfo7oKkP3cHP2nMSKhbfbk2a1e-xf6DREsf4wM-cTiO9n4R24WvUDDuqbSOtt2O9dm31rsZIgoveMuSBaI-X75FoRH08YaxiKgi9PLhE0xMNtQmaDA07AtWLXdHQ5X_I1g"
CASTING_DIRECTOR_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWZjZmQxMDBjN2YxMzYwMDc5ZmQwODk2IiwiYXVkIjoiY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjA3NDYwMjU1LCJleHAiOjE2MDc1NDY2NTUsImF6cCI6Ik1aRjBCVjc2NjZQTUk3Y3NkcXR4b0E3dnVMcnFQNjBGIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyJdfQ.MH0nqNEPiCJnG-3YISe6qo6RDX_kOsH1IA-z06WthasynnM5ppSKk3ZGm9gFyB6jNqsSZFlfTxEygsMPKfXJrUw3Hyu9WKJEKTgFnR2IDOH7PeXVaH3_NcXM6SblxYK9YZsHH-jBT0kP_jheambA_NhnYb0KIqdOaILG2s4BNbu1uC1TOWEKMIwBWNYFtAY7PQtKDjrYQFnfXLeT8YZ2q29ZD_cVxfoBdPaaonQl6rp_tJR1BIaeUuScUjfZI_U0cCpJ0Sztzer9p3ZjfVmUbVK8wSxFvkXvkh94xSiRnDdnBoOjEdMRo99a4E1_WEYPDa-hc-P1u4a4ffcKOzR-uQ"
NO_ROLE_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWZjZmU0YTA5YWJkNzAwMDZlNDFhM2JkIiwiYXVkIjoiY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjA3NDYwMTUwLCJleHAiOjE2MDc1NDY1NTAsImF6cCI6Ik1aRjBCVjc2NjZQTUk3Y3NkcXR4b0E3dnVMcnFQNjBGIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6W119.6tjtzNrUDm26VLH9TQj4ltUSsrZ_r_j8QLAdycXgO2SNfuy9w-fzPpy_gzGH-YSWrTdp4Y2AJGK3aB_9IU2Xh_Q9y-wpvH2KhvL3yi4NnH5g6J9rT1z17Eb8w6MfhQfm3_m82nc4xGjebDLcurSkZaxv9cQkfcrNDFqqUK_bilVujcV1-0twKBIUVC-eYOfiM91ELyIqQuqqBymPQvKpBoRlHMOUX3YviOP31nuWVY66bsUvzc-An6l2zL1m1qPKEvgQVDsTCvJQt873_FlrrkBZ3i6rWjITHJO9DBAK8CGeatklcBPWvhXoEdutdZ0v7EC9SZSkUq3bBrSeXKM3nw"

# ---------------------------------------------------------------------------#
# Test class
# ---------------------------------------------------------------------------#


class AgencyTestCase(unittest.TestCase):
    """This class represents the casting agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
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

    # ------------------------------------------------------------------------#
    # Test every endpoint.
    # ------------------------------------------------------------------------#

    # tests for the "GET /actors" endpoint
    def test_a_a_success_get_actors(self):
        res = self.client().get(
            '/actors',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue("actors" in data)

    def test_a_b_failure_no_auth(self):
        res = self.client().get(
            '/actors',
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']["description"],
                         "Authorization header is expected.")

    # tests for the "GET /movies" endpoint
    def test_b_a_success_get_movies(self):
        res = self.client().get(
            '/movies',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue("movies" in data)

    def test_b_b_failure_no_scope(self):
        res = self.client().get(
            '/movies',
            headers={"Authorization": "Bearer " + NO_ROLE_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']["description"],
                         "Permission not found.")

    # tests for the "POST /actors" endpoint
    def test_c_a_success_create_actor(self):
        res = self.client().post(
            '/actors',
            json=self.new_actor,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        check_actor = Actor.query.filter(
            Actor.name == data["actors"][0]["name"]).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(check_actor)

    def test_c_b_failure_no_name(self):
        res = self.client().post(
            '/actors',
            json=self.incomplete_actor,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # tests for the "POST /movies" endpoint
    def test_d_a_success_create_movie(self):
        res = self.client().post(
            '/movies',
            json=self.new_movie,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        check_movie = Movie.query.filter(
            Movie.title == data["movies"][0]["title"]).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])

    def test_d_b_failure_nonunique_title(self):
        res = self.client().post(
            '/movies',
            json=self.new_movie,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # tests for the "PATCH /actors/id" endpoint
    def test_e_a_success_update_actor(self):
        res = self.client().patch(
            '/actors/1',
            json=self.incomplete_actor,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])

    def test_e_b_failure_nonexistent_id(self):
        res = self.client().patch(
            '/actors/1111',
            json=self.incomplete_actor,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # tests for the "PATCH /movies/id" endpoint
    def test_f_a_success_update_movie(self):
        res = self.client().patch(
            '/movies/1',
            json=self.incomplete_movie,
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])

    def test_f_b_failure_invalid_date(self):
        res = self.client().patch(
            '/movies/1',
            json={"release_date": "August 10th, 1999"},
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # tests for the "DELETE /actors/id" endpoint
    def test_g_a_success_delete_actor(self):
        res = self.client().delete(
            '/actors/1',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])

    def test_g_b_failure_id_not_found(self):
        res = self.client().delete(
            '/actors/1111',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # tests for the "DELETE /movies/id" endpoint
    def test_h_a_success_delete_movie(self):
        res = self.client().delete(
            '/movies/1',
            headers={"Authorization": "Bearer " + EXECUTIVE_PRODUCER_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])

    def test_h_b_failure_no_auth(self):
        res = self.client().delete(
            '/movies/1'
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']["description"],
                         "Authorization header is expected.")

    # ------------------------------------------------------------------------#
    # RBAC tests for the Casting Assistant
    # ------------------------------------------------------------------------#

    # casting assistant SHOULD access get:actors endpoint
    def test_i_RBAC_get_actors(self):
        res = self.client().get(
            '/actors',
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue("actors" in data)

    # casting assistant SHOULD NOT access patch:actors endpoint
    def test_j_RBAC_cannot_update_actor(self):
        res = self.client().patch(
            '/actors/1',
            json=self.incomplete_actor,
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']["description"],
                         "Permission not found.")

    # ------------------------------------------------------------------------#
    # RBAC tests for the Casting Director
    # ------------------------------------------------------------------------#

    # casting director SHOULD access post:actors endpoint
    def test_k_RBAC_create_actor(self):
        res = self.client().post(
            '/actors',
            json=self.new_actor,
            headers={"Authorization": "Bearer " + CASTING_DIRECTOR_JWT}
        )
        data = json.loads(res.data)
        check_actor = Actor.query.filter(
            Actor.name == data["actors"][0]["name"]).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(check_actor)

    # casting director SHOULD NOT access post:movies endpoint
    def test_l_RBAC_cannot_create_movie(self):
        res = self.client().post(
            '/movies',
            json=self.new_movie,
            headers={"Authorization": "Bearer " + CASTING_DIRECTOR_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']["description"],
                         "Permission not found.")


# Make the tests conveniently executable
if __name__ == "__main__":
    db_drop_and_create_all()
    unittest.main()
