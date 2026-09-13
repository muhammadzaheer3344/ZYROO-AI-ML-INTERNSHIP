import os
import signal
import subprocess
import sys
import time


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    python_executable = sys.executable
    streamlit_process = subprocess.Popen(
        [python_executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        cwd=PROJECT_DIR,
    )
    fastapi_process = subprocess.Popen(
        [python_executable, "-m", "uvicorn", "fastapi_app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=PROJECT_DIR,
    )

    print("Streamlit: http://localhost:8501")
    print("FastAPI:   http://localhost:8000")
    print("API docs:  http://localhost:8000/docs")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            if streamlit_process.poll() is not None:
                raise RuntimeError("Streamlit stopped unexpectedly.")
            if fastapi_process.poll() is not None:
                raise RuntimeError("FastAPI stopped unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping both servers...")
    finally:
        for process in (streamlit_process, fastapi_process):
            if process.poll() is None:
                process.terminate()
        for process in (streamlit_process, fastapi_process):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
