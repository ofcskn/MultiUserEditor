import multiprocessing
import time
import sys
import os

from server.server import start_server
from client.client import start_client 

# Adjust import paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_server():
    print("🔌 Starting server...")
    start_server()  # Your server's main loop

def run_client():
    print("🖥️ Starting client...")
    time.sleep(2)  # Simulate GUI running time
    start_client()  # Your PySide6 GUI launcher

if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()

    try:
        run_client()
    finally:
        time.sleep(3)
        print("❌ Shutting down server...")
        server_process.terminate()
        server_process.join()
        print("Server process terminated.")