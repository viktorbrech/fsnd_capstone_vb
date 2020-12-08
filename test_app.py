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


# ---------------------------------------------------------------------------#
# JWTs for every role.
# ---------------------------------------------------------------------------#

EXECUTIVE_PRODUCER_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTcyNDg3MjI1OTI2MjExNDg0NzkiLCJhdWQiOlsiY2Fwc3RvbmVfYXBpIiwiaHR0cHM6Ly92YnJlY2guZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwNzM3NjM1NywiZXhwIjoxNjA3NDYyNzU3LCJhenAiOiJNWkYwQlY3NjY2UE1JN2NzZHF0eG9BN3Z1THJxUDYwRiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOm1vdmllcyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiLCJwb3N0Om1vdmllcyJdfQ.H_Q6oidHmEz7uQkJ2c41BSIiuYRvIRi0hUEdcfYmgNUxS43IW_WrY9qxun1JJD3blMG8zPzkTiOUCCqfuexvCYoyV_fBj73FsMeSSJg8u4frb30PcNNH-2MJAm3DPEK96kUTu6-Sx3rD0PmliBFfL4McCS83EW-AGNKnWfb6tjPApgM7op34l2vGC-H_ybUO26pWX8-BaVLfyFtRJVQHXjc4nDGlaA6LmAUCC87UlxZQvo0ewYi8E3_DK93zxaZaxISAfxyKOlEa9m-UUF6JRGl_3w1MfYVtN1_Y3wNp3oIzRVhv_swhmBh48sLeZdaohzHL0Gh--UsLvW0q8_laMQ"
CASTING_ASSISTANT_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTAyODk3MTA3MTk1MjkyNzczNjgiLCJhdWQiOlsiY2Fwc3RvbmVfYXBpIiwiaHR0cHM6Ly92YnJlY2guZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwNzM4MTI3MiwiZXhwIjoxNjA3NDY3NjcyLCJhenAiOiJNWkYwQlY3NjY2UE1JN2NzZHF0eG9BN3Z1THJxUDYwRiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyJdfQ.YdmaaCgrAVcejEwrJOOQ0XTOcN0-qS2VZCCuXu8VtV-PvupDWm45ke57xmFuJpOXkWhQQj4ftw8RWOMdDQLNqUZbJLfiWpfeGdqEQ_vsiGWwnNgAwmgJ_SupCEsx57dhGaWGq2vefDY0j2MYQ0HnZn1majjfFekHF0Gbkuf_HdQqekFIJP7KPlnUBgRUEZcnnpU5soUd_yn3C0sGJucTWhB_RCh7Jk5RP9vAyYrU096iXa3rI_ufzphvT3ZXAI1SA18U37UAwwsW5eBpCEcq2SOGsIa-Nav_hBV3w911KREBlczOAoh8SJh0UGpV_MNk1CqUjH0lwzvJd2xKgSYXLA"
CASTING_DIRECTOR_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDIzNjc5NTQwNjU4ODIxMDIyMzQiLCJhdWQiOlsiY2Fwc3RvbmVfYXBpIiwiaHR0cHM6Ly92YnJlY2guZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwNzM4MTM5MiwiZXhwIjoxNjA3NDY3NzkyLCJhenAiOiJNWkYwQlY3NjY2UE1JN2NzZHF0eG9BN3Z1THJxUDYwRiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyJdfQ.E8-ptWDosKcdhdDGh6K3qMYSkG7nQCuOkAdYyb0Njbm_JoGCMB0CRbLa6RlVfgTutF7TgKs1NvXiA7Qz4qauYSH1eXywiucGilonuk4OuL3JxKFnGiWyO4Vl3dIUwL-Cz4dQY3VQa63jJvDwa6x_sNkidyO5DJHniS1fnyp56svWEL7Lpa6mnj3IWnny_HDhJr3tnSZqRSlmzGmd_TH_ZNMfKIL1avBeDZ9DXwompa3y9u2fcCfj_9W7HXF65FBdV-uQ28Xx6hONo2ggoktMBmnO1UUrdvjoWZ2UfB8IO9SaTbmMGs9isNFaELefI8LHrbg_PLWjGiagtlCKhgKawQ"
NO_ROLE_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImVhVUZmWnhBaWpfUk9TR1M2Q05PYiJ9.eyJpc3MiOiJodHRwczovL3ZicmVjaC5ldS5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDIzNjc5NTQwNjU4ODIxMDIyMzQiLCJhdWQiOlsiY2Fwc3RvbmVfYXBpIiwiaHR0cHM6Ly92YnJlY2guZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwNzM3Njg5MywiZXhwIjoxNjA3NDYzMjkzLCJhenAiOiJNWkYwQlY3NjY2UE1JN2NzZHF0eG9BN3Z1THJxUDYwRiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.6QHhesapZe6BwMXzl-H-uQPGUTKqoyQq18gwm3_cJ4tdtVf-HKc7vzw-WtLSzkqGO2KfYabF-qeeXwgUuBdMWjMhUpfI9sGY6OkHDsYQZVcMS1SN56xWaKeM-OiqLTgyOTyyxTA7LwWjwWJpWhdhR_pnq4RribgBX8R2eOpjC_gKFtx-xxDqDXvF0_jqxS3I1NM8vuzTIuz0Zf_KDF0Wxjl3-efrlIw95nz2Bb2PkkNRowWizgvat_rr8Rl9UcNxv07ilcfaQbWmtPwDB6t-XToX_aACxTg5hmXS3rBRER9l7k5bDI0IUkYEqeMj5pusD-WgXOY3bok_lZhWYuosbw"

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

    # SHOULD access get:actors endpoint
    def test_i_RBAC_get_actors(self):
        res = self.client().get(
            '/actors',
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT_JWT}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue("actors" in data)

    # should NOT access patch:actors endpoint
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

    # SHOULD access post:actors endpoint
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

    # should NOT access post:movies endpoint
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
    unittest.main()
