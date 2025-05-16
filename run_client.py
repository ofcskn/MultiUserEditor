import sys
import os

from client.client import start_client 

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_client():
    print("🖥️ Starting client...")
    start_client()  # Your PySide6 GUI launcher

if __name__ == "__main__":
    try:
        run_client()
    finally:
        print("❌ Shutting down client...")
