"""
Quick test to verify Jarvis application is running
"""
import requests
import time

def test_server():
    """Test if server is running"""
    try:
        # Wait a moment for server to start
        time.sleep(2)
        
        # Test health check endpoint
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:5000")
        print("Make sure the application is running with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Jarvis server...")
    test_server()
