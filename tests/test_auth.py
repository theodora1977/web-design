import os
import tempfile
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///{0}".format(os.path.join(tempfile.gettempdir(), "auth_test.sqlite")))

from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import User


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_signup_creates_admin_account_and_allows_login(self):
        response = self.client.post(
            "/signup",
            data={"username": "adminuser", "password": "secret123", "confirm_password": "secret123"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "/admin/login")

        db = SessionLocal()
        try:
            created_user = db.query(User).filter(User.username == "adminuser").first()
        finally:
            db.close()

        self.assertIsNotNone(created_user)
        self.assertTrue(created_user.is_admin)

        login_response = self.client.post(
            "/admin/login",
            data={"username": "adminuser", "password": "secret123"},
            follow_redirects=False,
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.headers["location"], "/admin/dashboard")


if __name__ == "__main__":
    unittest.main()
