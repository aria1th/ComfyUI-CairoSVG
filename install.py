#https://github.com/ltdrdata/ComfyUI-Impact-Pack/blob/Main/install.py
import sys
import subprocess
import threading
import locale

def handle_stream(stream, is_stdout):
    stream.reconfigure(encoding=locale.getpreferredencoding(), errors='replace')

    for msg in stream:
        if is_stdout:
            print(msg, end="", file=sys.stdout)
        else: 
            print(msg, end="", file=sys.stderr)

def process_wrap(cmd_str, cwd=None, handler=None):
    process = subprocess.Popen(cmd_str, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    if handler is None:
        handler = handle_stream

    stdout_thread = threading.Thread(target=handler, args=(process.stdout, True))
    stderr_thread = threading.Thread(target=handler, args=(process.stderr, False))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    return process.wait()

if "python_embeded" in sys.executable or "python_embedded" in sys.executable: #standalone python version
    pip_install = [sys.executable, '-s', '-m', 'pip', 'install', "-U"]
else:
    pip_install = [sys.executable, '-m', 'pip', 'install', "-U"]

def initialization():
    requirements = read_requirements()
    for req in requirements:
        try:
            __import__(req)
            print(f"{req} already installed.")
        except ImportError:
            run_installation(req)

def read_requirements():
    import os
    cur_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(cur_path, "requirements.txt"), "r") as f:
        return f.read().splitlines()

def run_installation(pkg_name: str):
    print(f"Installing {pkg_name}...")
    if process_wrap(pip_install + [pkg_name]) == 0:
        print(f"Successfully installed {pkg_name}")
    else:
        print(f"Failed to install {pkg_name}")

if __name__ == "__main__":
    initialization()
    print("Installation completed.")
