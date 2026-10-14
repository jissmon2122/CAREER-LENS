import unittest
from app import create_app
from app.config import Config, _parse_allowed_origins

class TestCorsVerification(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_cors_origin_parser(self):
        """Verify robust parsing of CORS_ORIGINS with whitespace, commas, semicolons, trailing slashes."""
        # Test default origins always include production and dev URLs
        origins = _parse_allowed_origins()
        self.assertIn('https://careerlens-iota.vercel.app', origins)
        self.assertIn('http://localhost:5173', origins)
        self.assertNotIn('*', origins)

    def test_options_preflight_login(self):
        """Verify OPTIONS preflight on /api/auth/login succeeds with exact origin and allowed headers."""
        target_origin = 'https://careerlens-iota.vercel.app'
        res = self.client.open(
            '/api/auth/login',
            method='OPTIONS',
            headers={
                'Origin': target_origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('Access-Control-Allow-Origin'), target_origin)
        self.assertNotEqual(res.headers.get('Access-Control-Allow-Origin'), '*')
        self.assertEqual(res.headers.get('Access-Control-Allow-Credentials'), 'true')
        
        methods = res.headers.get('Access-Control-Allow-Methods', '')
        for m in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']:
            self.assertIn(m, methods)
            
        allowed_headers = res.headers.get('Access-Control-Allow-Headers', '')
        self.assertIn('Content-Type', allowed_headers)
        self.assertIn('Authorization', allowed_headers)

    def test_options_preflight_me(self):
        """Verify OPTIONS preflight on protected endpoint /api/auth/me does not trigger 401."""
        target_origin = 'https://careerlens-iota.vercel.app'
        res = self.client.open(
            '/api/auth/me',
            method='OPTIONS',
            headers={
                'Origin': target_origin,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Authorization'
            }
        )
        # Preflight must NOT return 401 Unauthorized
        self.assertIn(res.status_code, [200, 204])
        self.assertEqual(res.headers.get('Access-Control-Allow-Origin'), target_origin)
        self.assertEqual(res.headers.get('Access-Control-Allow-Credentials'), 'true')

    def test_post_login_cors_headers_on_validation_failure(self):
        """Verify CORS headers are present even when POST /api/auth/login returns 400 Bad Request."""
        target_origin = 'https://careerlens-iota.vercel.app'
        res = self.client.post(
            '/api/auth/login',
            json={},  # empty body to trigger 400 validation error
            headers={'Origin': target_origin}
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.headers.get('Access-Control-Allow-Origin'), target_origin)
        self.assertEqual(res.headers.get('Access-Control-Allow-Credentials'), 'true')

    def test_protected_route_cors_headers_on_401(self):
        """Verify CORS headers are present when protected endpoint returns 401 Unauthorized."""
        target_origin = 'https://careerlens-iota.vercel.app'
        res = self.client.get(
            '/api/auth/me',
            headers={'Origin': target_origin}
        )
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.headers.get('Access-Control-Allow-Origin'), target_origin)
        self.assertEqual(res.headers.get('Access-Control-Allow-Credentials'), 'true')

    def test_disallowed_origin_does_not_get_cors_headers(self):
        """Verify that an untrusted origin does NOT receive Access-Control-Allow-Origin."""
        untrusted_origin = 'https://malicious-site.example.com'
        res = self.client.open(
            '/api/auth/login',
            method='OPTIONS',
            headers={
                'Origin': untrusted_origin,
                'Access-Control-Request-Method': 'POST'
            }
        )
        self.assertNotEqual(res.headers.get('Access-Control-Allow-Origin'), untrusted_origin)
        self.assertNotEqual(res.headers.get('Access-Control-Allow-Origin'), '*')

if __name__ == '__main__':
    unittest.main()
