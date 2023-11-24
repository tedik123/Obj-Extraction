import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from timeit import default_timer as timer
from datetime import timedelta

MAIN_PYTHON_FILE_NAME = "ImageViewer.py"
VENV_PATH = "../../venv/Scripts/python.exe"

# Define the input and output directories
ui_dir = "designer"
generated_dir = "../../generated_design/generated"

DIRECTORY_TO_WATCH = "../../pixels and uv stuff/GUI"
PROCESS = None


class CodeChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        start = timer()

        compile_ui = True

        if event.is_directory:
            return
        # I wish there was a way for a watcher to ignore anything in pycache
        if "__pycache__" in event.src_path:
            # print("IGNORED")
            return
        if event.src_path.endswith(".ui"):
            compile_ui = True
        if event.event_type == "modified":
            # get file name
            file_name = os.path.basename(event.src_path)
            print(f"Noticed modifications in {file_name}")

        print(event)
        print(f'Code changed: {event.src_path}')
        restart_app(compile_ui)

        end = timer()
        print("Recompiled in: ", timedelta(seconds=end - start))


def snake_to_title(snake_str):
    words = snake_str.split('_')
    title_words = [word.capitalize() for word in words]
    return ''.join(title_words)


def convert_ui_files():
    # List all .ui files in the input directory
    ui_files = [f for f in os.listdir(ui_dir) if f.endswith(".ui")]
    for ui_file in ui_files:
        input_path = os.path.join(ui_dir, ui_file)
        output_file = snake_to_title(os.path.splitext(ui_file)[0]) + ".py"
        output_path = os.path.join(generated_dir, output_file)
        # Run the pyuic6 command to convert .ui to .py
        pyuic6_command = f"pyuic6 {input_path} -o {output_path}"
        try:
            subprocess.run(pyuic6_command, shell=True, check=True)
            print(f"Converted {ui_file} to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {ui_file}: {e}")
    print("Conversion complete.")


def restart_app(compile_ui=False):
    global PROCESS
    if PROCESS:
        # Kill the existing process
        PROCESS.terminate()
        PROCESS = None

    if compile_ui:
        # convert all .ui files to .py
        convert_ui_files()

    # Start a new process
    PROCESS = subprocess.Popen([VENV_PATH, MAIN_PYTHON_FILE_NAME])


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(CodeChangeHandler(), path=DIRECTORY_TO_WATCH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
