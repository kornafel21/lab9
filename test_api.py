from flask_testing import TestCase

from base64 import b64encode

from app import app

from models import *


class BaseTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        super().setUp()
        self.create_tables()

        self.admin_create = {"username": "den55", "first_name": "Den", "last_name": "James",
                             "email": "denjam@gmail.com",
                             "password": "123456", "phone": "380671234567"}
        self.admin_login = {"username": "den55", "password": "123456"}

        self.moderator_create = {"username": "kate228", "first_name": "Kate", "last_name": "Jonson", "email":
                                 "katjon@gmail.com", "password": "1111", "phone": "380671234567"}

        self.moderator_login = {"username": "kate228", "password": "1111"}

        self.user_create = {"username": "margo2507", "first_name": "Margo", "last_name": "Colson", "email":
                            "marcol@gmail.com", "password": "25072000m", "phone": "380671234567"}

        self.user_login = {"username": "margo2507", "password": "25072000m"}

        self.article_create = {"name": "News 2.0", "text": "Something big happened."}

        self.change_create = {"article_id": 1, "new_text": "Something big happened. And the UFO was in the lead."}

        self.review_positive = {"change_id": 1, "verdict": 1, "comment": "All is good"}

        self.review_negative = {"change_id": 1, "verdict": 0, "comment": "Too many mistakes"}

    def tearDown(self):
        Session().close()

    def create_tables(self):
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

    def auth_header(self, credentials):
        token = b64encode(f"{credentials['username']}:{credentials['password']}".encode('utf-8')).decode("ascii")
        return {'Authorization': f'Basic {token}'}

    def create_from_admin_to_change(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        self.client.post('/api/change', json=self.change_create, headers=self.auth_header(self.admin_login))

    def create_from_admin_to_review(self):
        self.create_from_admin_to_change()
        self.client.post('/api/review', json=self.review_negative, headers=self.auth_header(self.admin_login))


class TestHelloWorld(BaseTestCase):
    def test_hello_world(self):
        response = self.client.get('/api/hello-world')

        self.assertEqual(response.text, 'Hello World!')

    def test_hello_world_5(self):
        response = self.client.get('/api/hello-world-5')

        self.assertEqual(response.text, 'Hello World 5')


class TestUser(BaseTestCase):
    def test_create(self):
        response = self.client.post('/api/user', json=self.admin_create)

        self.assertEqual(response.status_code, 200)

    def test_create_not_enough_data(self):
        response = self.client.post('/api/user', json={'username': 'james'})

        self.assertEqual(response.status_code, 400)

    def test_create_username_already_used(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.post('/api/user', json=self.admin_create)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, '{"error":{"code":400,"message":"Username already used","type":"Validation"}}'
                                        '\n')

    def test_update(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.put('/api/user/1', json={"first_name": "Denya", "phone": "380676666666"},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_update_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        response = self.client.put('/api/user/1', json={"first_name": "Denya", "phone": "380676666666"},
                                   headers=self.auth_header(self.user_login))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.get('/api/user/1', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_get_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        response = self.client.get('/api/user/1', headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 403)

    def test_get_unauthorized(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.get('/api/user/1')

        self.assertEqual(response.status_code, 403)

    def test_get_not_found(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.get('/api/user/15', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)

    def test_update_user_status(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        response = self.client.put('/api/user/changeStatus/2', json={'user_status': 1},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_update_user_status_not_found(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.put('/api/user/changeStatus/20', json={'user_status': 1},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)

    def test_update_user_status_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        response = self.client.put('/api/user/changeStatus/1', json={'user_status': 1},
                                   headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 403)

    def test_update_user_status_last_admin(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.put('/api/user/changeStatus/1', json={'user_status': 2},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 400)

    def test_update_user_status_wrong_status(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        response = self.client.put('/api/user/changeStatus/2', json={'user_status': 15},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, '{"error":{"code":400,"message":"Wrong user status. Must be 0, 1 or 2",'
                                        '"type":"Validation"}}\n')

    def test_login(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.get('/api/user/login', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"id":1,"role":"admin"}\n')

    def test_login_moderator(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.moderator_create)
        self.client.put('/api/user/changeStatus/2', json={'user_status': 1}, headers=self.auth_header(self.admin_login))

        response = self.client.get('/api/user/login', headers=self.auth_header(self.moderator_login))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"id":2,"role":"moderator"}\n')

    def test_login_user(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)

        response = self.client.get('/api/user/login', headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"id":2,"role":"user"}\n')

    def test_delete(self):
        self.create_from_admin_to_review()

        response = self.client.delete('/api/user/1', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 200)

    def test_delete_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)

        response = self.client.delete('/api/user/1', headers=self.auth_header(self.user_login))
        self.assertEqual(response.status_code, 403)


class TestArticle(BaseTestCase):
    def test_create(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.post('/api/article', json=self.article_create,
                                    headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_create_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        response = self.client.post('/api/article', json=self.article_create,
                                    headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 403)

    def test_get(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        response = self.client.get('/api/article/1')

        self.assertEqual(response.status_code, 200)

    def test_get_not_found(self):
        response = self.client.get('/api/article/10')

        self.assertEqual(response.status_code, 404)

    def test_update(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        response = self.client.put('/api/article/1', json={"name": "News 2.0", "text": "Something big happened."},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_update_not_found(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.put('/api/article/15', json={"name": "News 2.0", "text": "Something big happened."},
                                   headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)

    def test_update_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        response = self.client.put('/api/article/1', json={"name": "News 2.0", "text": "Something big has happened."},
                                   headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 403)

    def test_delete(self):
        self.create_from_admin_to_review()

        response = self.client.delete('/api/article/1', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 200)

    def test_delete_not_found(self):
        self.client.post('/api/user', json=self.admin_create)

        response = self.client.delete('/api/article/1', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 404)

    def test_delete_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))

        response = self.client.delete('/api/article/1', headers=self.auth_header(self.user_login))
        self.assertEqual(response.status_code, 403)


class TestChange(BaseTestCase):
    def test_create(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        response = self.client.post('/api/change', json=self.change_create, headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_create_article_not_found(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.post('/api/change', json=self.change_create, headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)

    def test_get(self):
        self.create_from_admin_to_change()

        response = self.client.get('/api/change/1', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_get_forbidden(self):
        self.create_from_admin_to_change()

        self.client.post('/api/user', json=self.user_create)
        response = self.client.get('/api/change/1', headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 403)

    def test_get_not_found(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.get('/api/change/1', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        self.create_from_admin_to_review()

        response = self.client.delete('/api/change/1', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 200)

    def test_delete_forbidden(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/user', json=self.user_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        self.client.post('/api/change', json=self.change_create, headers=self.auth_header(self.admin_login))

        response = self.client.delete('/api/change/1', headers=self.auth_header(self.user_login))
        self.assertEqual(response.status_code, 403)

    def test_delete_not_found(self):
        self.client.post('/api/user', json=self.admin_create)

        response = self.client.delete('/api/change/15', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 404)

    def test_my_changes(self):
        self.create_from_admin_to_change()
        self.client.post('/api/change', json=self.change_create, headers=self.auth_header(self.admin_login))

        response = self.client.get('/api/mychanges', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '[{"article_id":1,"article_version":0,"id":1,"new_text":"Something big '
                                        'happened. And the UFO was in the lead.","old_text":"Something big '
                                        'happened.","proposer_id":1,"status":"in review"},{"article_id":1,'
                                        '"article_version":0,"id":2,"new_text":"Something big happened. And the UFO '
                                        'was in the lead.","old_text":"Something big happened.","proposer_id":1,'
                                        '"status":"in review"}]\n')

    def test_changes_in_review(self):
        self.create_from_admin_to_change()

        response = self.client.get('/api/changesInReview', headers=self.auth_header(self.admin_login))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '[{"article_id":1,"article_version":0,"id":1,"new_text":"Something big '
                                        'happened. And the UFO was in the lead.","old_text":"Something big '
                                        'happened.","proposer_id":1,"status":"in review"}]\n')

    def test_changes_in_review_forbidden(self):
        self.create_from_admin_to_change()
        self.client.post('/api/user', json=self.user_create)

        response = self.client.get('/api/changesInReview', headers=self.auth_header(self.user_login))
        self.assertEqual(response.status_code, 403)


class TestReview(BaseTestCase):
    def test_create(self):
        self.create_from_admin_to_change()
        response = self.client.post('/api/review', json=self.review_positive,
                                    headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_create_change_not_found(self):
        self.client.post('/api/user', json=self.admin_create)
        response = self.client.post('/api/review', json=self.review_positive,
                                    headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, '{"error":{"code":404,"message":"Change not found","type":"NOT_FOUND"}}\n')

    def test_create_forbidden(self):
        self.create_from_admin_to_change()
        self.client.post('/api/user', json=self.user_create)
        response = self.client.post('/api/review', json=self.review_positive,
                                    headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 403)

    def test_create_already_exist(self):
        self.create_from_admin_to_review()
        response = self.client.post('/api/review', json=self.review_positive,
                                    headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, '{"error":{"code":400,"message":"Review already exist","type":"BAD_REQUEST"}}'
                                        '\n')

    def test_get(self):
        self.create_from_admin_to_review()
        self.client.post('/api/user', json=self.user_create)
        response = self.client.get('/api/review/1', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)

    def test_get_not_found(self):
        self.client.post('/api/user', json=self.admin_create)

        response = self.client.get('/api/review/15', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 404)

    def test_my_reviews(self):
        self.create_from_admin_to_review()
        response = self.client.get('/api/myReviews', headers=self.auth_header(self.admin_login))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '[{"change_id":1,"comment":"Too many mistakes","id":1,"reviewer_id":1,'
                                        '"verdict":false}]\n')

    def test_my_changes_reviewed(self):
        self.client.post('/api/user', json=self.admin_create)
        self.client.post('/api/article', json=self.article_create, headers=self.auth_header(self.admin_login))
        self.client.post('/api/user', json=self.user_create)
        self.client.post('/api/change', json=self.change_create, headers=self.auth_header(self.user_login))
        self.client.post('/api/review', json=self.review_positive, headers=self.auth_header(self.admin_login))
        response = self.client.get('/api/myChangesReviewed', headers=self.auth_header(self.user_login))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '[{"change_id":1,"comment":"All is good","id":1,"reviewer_id":1,'
                                        '"verdict":true}]\n')
