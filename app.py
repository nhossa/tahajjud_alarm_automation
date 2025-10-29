import sys
import requests

def should_program_run(timeout_sec=5):
    """Check if the system is online by making a request to a reliable website."""
    try:
        response = requests.get("https://www.google.com", timeout=timeout_sec)
        if response.status_code == 200:
            print("System is online. Proceeding with operations.")
            return True
    except Exception as e:
        print(f"Offline check failed: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    should_program_run()
    



