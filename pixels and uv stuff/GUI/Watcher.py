import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MAIN_PYTHON_FILE_NAME = "ImageViewer.py"
VENV_PATH = "../../venv/Scripts/python.exe"

PROCESS = None


class CodeChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        print(f'Code changed: {event.src_path}')
        restart_app()


def restart_app():
    global PROCESS
    if PROCESS:
        # Kill the existing process
        PROCESS.terminate()
        PROCESS = None

    # Start a new process
    PROCESS = subprocess.Popen([VENV_PATH, MAIN_PYTHON_FILE_NAME])


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(CodeChangeHandler(), path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
