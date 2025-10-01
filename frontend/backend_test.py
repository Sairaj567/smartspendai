import requests
import sys
import json
import time
from datetime import datetime

class SpendSmartAPITester:
    def __init__(self, base_url="https://spendsmart-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_user_id = "test_user_12345"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_test(name, False, error_msg)
                return False, {}

        except requests.exceptions.Timeout:
            self.log_test(name, False, f"Request timeout after {timeout}s")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error - service may be down")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_generate_demo_transactions(self):
        """Test generating demo transactions"""
        return self.run_test(
            "Generate Demo Transactions",
            "POST",
            f"transactions/generate/{self.test_user_id}",
            200
        )

    def test_get_spending_summary(self):
        """Test getting spending summary"""
        return self.run_test(
            "Get Spending Summary",
            "GET",
            f"analytics/spending-summary/{self.test_user_id}",
            200
        )

    def test_get_spending_trends(self):
        """Test getting spending trends"""
        return self.run_test(
            "Get Spending Trends",
            "GET",
            f"analytics/spending-trends/{self.test_user_id}",
            200
        )

    def test_get_user_transactions(self):
        """Test getting user transactions"""
        return self.run_test(
            "Get User Transactions",
            "GET",
            f"transactions/{self.test_user_id}",
            200
        )

    def test_create_transaction(self):
        """Test creating a new transaction"""
        transaction_data = {
            "user_id": self.test_user_id,
            "amount": 500.0,
            "category": "Food & Dining",
            "description": "Test restaurant payment",
            "merchant": "Test Restaurant",
            "type": "expense",
            "payment_method": "UPI"
        }
        
        return self.run_test(
            "Create Transaction",
            "POST",
            "transactions",
            200,
            data=transaction_data
        )

    def test_generate_ai_insights(self):
        """Test generating AI insights (may take longer due to Gemini API)"""
        print("\n⚠️  AI Insights test may take 10-30 seconds due to Gemini 2.5 Pro processing...")
        return self.run_test(
            "Generate AI Insights",
            "POST",
            f"ai/insights/{self.test_user_id}",
            200,
            timeout=60  # Longer timeout for AI processing
        )

    def test_get_ai_insights(self):
        """Test getting AI insights"""
        return self.run_test(
            "Get AI Insights",
            "GET",
            f"ai/insights/{self.test_user_id}",
            200
        )

    def test_create_upi_payment(self):
        """Test creating UPI payment intent"""
        payment_data = {
            "amount": 1000.0,
            "payee_name": "Test Payee",
            "payee_vpa": "testpayee@upi",
            "description": "Test payment",
            "user_id": self.test_user_id
        }
        
        success, response = self.run_test(
            "Create UPI Payment Intent",
            "POST",
            "payments/upi-intent",
            200,
            data=payment_data
        )
        
        if success and 'transaction_id' in response:
            # Test payment callback
            transaction_id = response['transaction_id']
            self.run_test(
                "UPI Payment Callback",
                "POST",
                f"payments/callback/{transaction_id}?status=success",
                200
            )
        
        return success, response

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting SpendSmart AI Backend API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)

        # Test basic connectivity
        self.test_root_endpoint()
        
        # Test transaction generation (needed for other tests)
        self.test_generate_demo_transactions()
        
        # Test analytics endpoints
        self.test_get_spending_summary()
        self.test_get_spending_trends()
        
        # Test transaction endpoints
        self.test_get_user_transactions()
        self.test_create_transaction()
        
        # Test AI insights (this might take longer)
        self.test_generate_ai_insights()
        time.sleep(2)  # Brief pause before getting insights
        self.test_get_ai_insights()
        
        # Test payment flow
        self.test_create_upi_payment()

        # Print final results
        print("\n" + "=" * 60)
        print("📊 BACKEND API TEST RESULTS")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = SpendSmartAPITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save test results
        with open('/app/test_reports/backend_test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0,
                'test_results': tester.test_results
            }, f, indent=2)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())