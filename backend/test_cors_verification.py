import unittest
from app import create_app

class TestCorsVerification(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_cors_preflight_and_responses(self):
        origins_to_test = [
            'https://careerlens-iota.vercel.app',
            'https://any-branch-preview.vercel.app',
            'http://localhost:5173',
            'http://127.0.0.1:5173'
        ]

        routes_to_test = [
            ('/api/auth/login', 'POST'),
            ('/api/auth/register', 'POST'),
            ('/api/jobs/recommended', 'GET'),
            ('/api/jobs/search', 'GET'),
            ('/api/health', 'GET'),
            ('/health', 'GET')
        ]

        for origin in origins_to_test:
            for route, method in routes_to_test:
                # Test OPTIONS preflight
                res = self.client.open(
                    route,
                    method='OPTIONS',
                    headers={
                        'Origin': origin,
                        'Access-Control-Request-Method': method,
                        'Access-Control-Request-Headers': 'Content-Type, Authorization'
                    }
                )
                self.assertEqual(res.status_code, 200, f"OPTIONS {route} failed with {res.status_code}")
                self.assertEqual(
                    res.headers.get('Access-Control-Allow-Origin'),
                    origin,
                    f"CORS header missing or mismatched for {origin} on OPTIONS {route}"
                )
                self.assertIn('POST', res.headers.get('Access-Control-Allow-Methods', ''))
                self.assertIn('Content-Type', res.headers.get('Access-Control-Allow-Headers', ''))

                # Test standard request
                res_actual = self.client.open(route, method=method, headers={'Origin': origin})
                self.assertEqual(
                    res_actual.headers.get('Access-Control-Allow-Origin'),
                    origin,
                    f"CORS header missing or mismatched for {origin} on {method} {route}"
                )

if __name__ == '__main__':
    unittest.main()
