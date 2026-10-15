import datetime
import unittest
import uuid
from unittest.mock import patch
import jwt

from app import create_app
from app.config import Config
from app.db import Database
from app.models.user import UserModel


class TestAuthResilience(unittest.TestCase):
    """Automated tests for CareerLens Authentication resilience, timeouts, and error handling."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True

    def setUp(self):
        self.client = self.app.test_client()
        self.test_email = f"resilience_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "SecurePassword123!"

        self.user_doc = UserModel.create_user({
            "name": "Resilience Test User",
            "email": self.test_email,
            "password": self.test_password,
            "education": "University",
            "degree": "B.S.",
            "preferred_job_role": "Software Engineer",
            "preferred_location": "Remote",
            "experience_level": "Mid-Level"
        })
        self.user_id = str(self.user_doc["_id"])

    def tearDown(self):
        coll = UserModel.get_collection()
        if coll is not None:
            try:
                coll.delete_one({"email": self.test_email})
            except Exception:
                pass
        UserModel._in_memory_users.pop(self.test_email, None)
        UserModel._in_memory_users.pop(self.user_id, None)

    def test_valid_login(self):
        """Test 1: Valid credentials login successfully with token and user object."""
        res = self.client.post('/api/auth/login', json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("token", data.get("data", {}))
        self.assertEqual(data["data"]["user"]["email"], self.test_email)

    def test_successful_get_me(self):
        """Test 2: Successful GET /api/auth/me with valid JWT token."""
        # Log in to get token
        login_res = self.client.post('/api/auth/login', json={
            "email": self.test_email,
            "password": self.test_password
        })
        token = login_res.get_json()["data"]["token"]

        # Call /api/auth/me
        me_res = self.client.get('/api/auth/me', headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data.get("success"))
        self.assertEqual(me_data["data"]["user"]["email"], self.test_email)
        self.assertEqual(me_data["data"]["user"]["name"], "Resilience Test User")

    def test_expired_token(self):
        """Test 3: Expired JWT token returns HTTP 401 with Token Expired message."""
        past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)
        expired_payload = {
            "sub": self.user_id,
            "email": self.test_email,
            "name": "Resilience Test User",
            "iat": past - datetime.timedelta(hours=1),
            "exp": past
        }
        expired_token = jwt.encode(expired_payload, Config.JWT_SECRET_KEY, algorithm="HS256")

        res = self.client.get('/api/auth/me', headers={
            "Authorization": f"Bearer {expired_token}"
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data.get("success"))
        self.assertIn("expired", data.get("message", "").lower())

    def test_database_unavailable_during_login(self):
        """Test 4a: Database unavailability returns HTTP 503 instead of 401 or 500 on login."""
        with patch.object(Database, 'is_connected', return_value=False), \
             patch.object(UserModel, '_in_memory_users', {}):
            res = self.client.post('/api/auth/login', json={
                "email": "offline_db_user@example.com",
                "password": "Password123!"
            })
            self.assertEqual(res.status_code, 503)
            data = res.get_json()
            self.assertFalse(data.get("success"))
            self.assertEqual(data.get("error"), "Database unavailable")

    def test_database_unavailable_during_get_me(self):
        """Test 4b: Database unavailability returns HTTP 503 instead of 401 during token verification."""
        # Generate valid token
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": "507f1f77bcf86cd799439011",
            "email": "some_remote_user@example.com",
            "name": "Remote Candidate",
            "iat": now,
            "exp": now + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

        with patch.object(Database, 'is_connected', return_value=False), \
             patch.object(UserModel, '_in_memory_users', {}):
            res = self.client.get('/api/auth/me', headers={
                "Authorization": f"Bearer {token}"
            })
            self.assertEqual(res.status_code, 503)
            data = res.get_json()
            self.assertFalse(data.get("success"))
            self.assertEqual(data.get("error"), "Database unavailable")

    def test_missing_and_malformed_auth_header(self):
        """Test 5: Missing or malformed Authorization header returns HTTP 401."""
        # Missing header
        res1 = self.client.get('/api/auth/me')
        self.assertEqual(res1.status_code, 401)
        self.assertIn("missing", res1.get_json().get("message", "").lower())

        # Malformed header (not Bearer)
        res2 = self.client.get('/api/auth/me', headers={"Authorization": "Basic abcdef123"})
        self.assertEqual(res2.status_code, 401)
        self.assertIn("format", res2.get_json().get("message", "").lower())

    def test_cors_preflight_on_auth_endpoints(self):
        """Test 6: OPTIONS preflight on /api/auth/login and /api/auth/me returns 200/204 with CORS headers."""
        for endpoint in ['/api/auth/login', '/api/auth/me']:
            res = self.client.open(
                endpoint,
                method='OPTIONS',
                headers={
                    'Origin': 'https://careerlens-iota.vercel.app',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type, Authorization'
                }
            )
            self.assertIn(res.status_code, [200, 204])
            self.assertEqual(
                res.headers.get('Access-Control-Allow-Origin'),
                'https://careerlens-iota.vercel.app'
            )


if __name__ == '__main__':
    unittest.main()
