import time
import sys
import os

from client.client import start_client 

# Adjust import paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_client():
    print("🖥️ Starting client...")
    time.sleep(2)  # Simulate GUI running time
    start_client()  # Your PySide6 GUI launcher

if __name__ == "__main__":
    try:
        run_client()
    finally:
        print("❌ Shutting down client...")
