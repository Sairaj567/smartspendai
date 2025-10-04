import requests
import os

# Test the import endpoint
url = "http://localhost:8000/api/transactions/import/test_user"
csv_file_path = "test_transactions.csv"

try:
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('test_transactions.csv', f, 'text/csv')}
        response = requests.post(url, files=files)
        
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except FileNotFoundError:
    print(f"File {csv_file_path} not found. Current directory: {os.getcwd()}")
    print("Files in current directory:", os.listdir('.'))
except requests.exceptions.ConnectionError:
    print("Could not connect to the server. Make sure the backend is running on port 8000.")
except Exception as e:
    print(f"Error: {e}")