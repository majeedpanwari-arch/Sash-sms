import unittest
import time
from app import create_app, db
from app.services.rate_limiter import rate_limiter

class RateLimiterTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['RATELIMIT_AUTH_LIMIT'] = 3
        self.app.config['RATELIMIT_AUTH_WINDOW'] = 60
        self.app.config['AUTH_BACKOFF_INITIAL_DELAY'] = 1.0
        self.app.config['AUTH_BACKOFF_FACTOR'] = 2.0
        self.client = self.app.test_client()

    def test_auth_exponential_backoff(self):
        print("\n--- Testing Auth Exponential Backoff ---")
        username = "test_backoff_user"
        
        with self.app.test_request_context('/', environ_base={'REMOTE_ADDR': '192.168.1.100'}):
            # 1. Initially not blocked
            is_blocked, remaining = rate_limiter.check_auth_exponential_backoff(username)
            self.assertFalse(is_blocked)

            # 2. Record 1st failure -> 1.0s delay
            rate_limiter.record_auth_failure(username)
            is_blocked, remaining = rate_limiter.check_auth_exponential_backoff(username)
            self.assertTrue(is_blocked)
            print(f"1st Failure Penalty Remaining: {remaining}s")

            # 3. Record 2nd failure -> 2.0s delay (1.0 * 2^1)
            rate_limiter.record_auth_failure(username)
            is_blocked, remaining = rate_limiter.check_auth_exponential_backoff(username)
            self.assertTrue(is_blocked)
            self.assertGreaterEqual(remaining, 1)
            print(f"2nd Failure Penalty Remaining: {remaining}s")

            # 4. Successful login resets backoff
            rate_limiter.record_auth_success(username)
            is_blocked, remaining = rate_limiter.check_auth_exponential_backoff(username)
            self.assertFalse(is_blocked)
            print("Successful login cleared backoff: OK ✅")

if __name__ == '__main__':
    unittest.main()
