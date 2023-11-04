import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MAIN_PYTHON_FILE_NAME = "ImageViewer.py"
VENV_PATH = "../../venv/Scripts/python.exe"

# Define the input and output directories
ui_dir = "designer"
generated_dir = "../../generated_design/generated"

DIRECTORY_TO_WATCH = "../../pixels and uv stuff/GUI"
PROCESS = None



class CodeChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return

        print(f'Code changed: {event.src_path}')
        restart_app()


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
        # Run the pyuic5 command to convert .ui to .py
        pyuic5_command = f"pyuic5 {input_path} -o {output_path}"
        try:
            subprocess.run(pyuic5_command, shell=True, check=True)
            print(f"Converted {ui_file} to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {ui_file}: {e}")
    print("Conversion complete.")


def restart_app():
    global PROCESS
    if PROCESS:
        # Kill the existing process
        PROCESS.terminate()
        PROCESS = None

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
