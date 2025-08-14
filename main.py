import io

from flask import Flask, send_from_directory, send_file, request, session, redirect
from flask import request
import subprocess
import tempfile
from json import dumps
import os
from random import choice
from dotenv import load_dotenv

load_dotenv()

SAFETY_KEY = os.getenv('SAFETY_KEY')
if SAFETY_KEY is None:
    print("NO \"SAFETY_KEY\" IN .env ALERT ALERT BAD BAD SET IT NOW")
    exit(1)


SECRET_KEY = os.getenv('SECRET_KEY')
if SECRET_KEY is None:
    print("NO \"SECRET_KEY\" IN .env ALERT ALERT BAD BAD SET IT NOW")
    exit(1)


print("todo use python executable env var for running and not just compression")  # todo
PYTHON_EXECUTABLE = os.getenv('PYTHON_EXECUTABLE')
if PYTHON_EXECUTABLE is None:
    print("using default python executable python3")
    PYTHON_EXECUTABLE = "python3"


def auth_required(func):
    def wrapper(*args, **kwargs):
        if "auth" not in session or not session["auth"]:
            raise PermissionError('Unauthorized', 401)
        return func(*args, **kwargs)
    return wrapper


app = Flask(__name__)
os.makedirs("./best", exist_ok=True)


def execute_task(task, timeout):
    print(timeout)
    try:
        proc = subprocess.run(['python3', 'run-task.py', str(task)], capture_output=True, timeout=timeout, text=True, encoding='latin-1')
        if proc.returncode != 0:
            status_code = 500
            output = proc.stderr
        else:
            status_code = 200
            output = proc.stdout
    except subprocess.TimeoutExpired:
        status_code = 501
        output = f"Code timed out after {timeout} seconds."
    except Exception as e:
        status_code = 502
        output = repr(e)

    return output, status_code


@app.route('/')
def home():
    if "auth" not in session or not session["auth"]:
        return send_file("./auth.html")
    return send_file("./index.html")


@app.post('/auth')
def auth():
    if request.data.decode('latin-1') == SAFETY_KEY:
        session["auth"] = True
        return 'come on through', 200
    return 'nope', 401


@auth_required
@app.route('/style.css')
def swag():
    return send_file("./style.css")


@auth_required
@app.route('/cm6.bundle.min.js')
def cm6():
    return send_file("./cm6.bundle.min.js", mimetype="application/javascript")


@auth_required
@app.route('/bundle.js')
def script():
    return send_file("./bundle.js", mimetype="application/javascript")


@auth_required
@app.route('/consolas.ttf')
def consolas():
    return send_file("./consolas.ttf", mimetype="font/ttf")


@auth_required
@app.route('/working/<path:filepath>')
def working(filepath):
    os.makedirs("working", exist_ok=True)
    return send_from_directory("./working/", filepath, mimetype='image/png')


@auth_required
@app.route('/infos/<path:filepath>')
def infos(filepath):
    return send_from_directory("./infos/", filepath, mimetype='application/json')


@app.route('/legend.png')
def legend():
    return send_file("./legend.png", mimetype='image/png')


@app.route('/favicon.ico')
def fav():
    return send_file("./favicon.ico", mimetype='image/ico')


@auth_required
@app.post('/run/<int:task>')
def run(task):
    os.makedirs("working/actual", exist_ok=True)
    os.makedirs("working/expected", exist_ok=True)
    os.makedirs("working/task_with_imports", exist_ok=True)
    fpath = f"./sols/task{task:03d}.py"
    with open(fpath, 'wb') as f:
        data = bytes.fromhex(request.data.decode()).replace(b'\x0d\x0a', b'\x0a')
        print(data)
        f.write(data)

    timeout = 90 if request.headers.get('x-long-timeout', "false") == "true" else 20
    output, status_code = execute_task(task, timeout)
    if len(request.data) == 0:
        os.remove(fpath)
    return output, status_code


@auth_required
@app.get('/view/<int:task>')
def view(task):
    os.makedirs("working/view", exist_ok=True)
    if not os.path.isfile(f"./working/view/task{task:03d}.png"):
        subprocess.check_output(['python3', 'view-task.py', str(task)])
    return send_from_directory("./working/view/", f"task{task:03d}.png", mimetype='image/png')


@auth_required
@app.get('/best/<int:task>')
def best(task):
    try:
        with open(f"./best/task{task:03d}.py", 'rb') as f:
            data = f.read()
        return data.hex(), 200
    except FileNotFoundError:
        return "not found oops", 500


@auth_required
@app.get('/viewtc/<int:task>/<int:testcase>')
def viewtc(task, testcase):
    os.makedirs("working/viewtc", exist_ok=True)
    if not os.path.isfile(f"./working/viewtc/task{task:03d}-{testcase}.png"):
        subprocess.check_output(['python3', 'view-task-tc.py', str(task), str(testcase)])
    return send_from_directory("./working/viewtc/", f"task{task:03d}-{testcase}.png", mimetype='image/png')


@auth_required
@app.get('/tools/list')
def list_tools():
    if not os.path.isdir("compression"):
        os.system("git clone https://github.com/jailctf-merger-goog-golf/compression")
    return dumps(os.listdir("compression/options")), 200


@auth_required
@app.post('/tools/run/<path:filepath>')
def do_tool(filepath):
    if not os.path.isdir("tools"):
        os.system("git clone https://github.com/jailctf-merger-goog-golf/compression")

    TIMEOUT = 12  # seconds
    stderr = "stderr"
    stdout = "stdout"
    data = request.data.decode()
    with tempfile.NamedTemporaryFile(mode='wb', suffix=".py", delete=False) as f:
        f.write(bytes.fromhex(data))
        f.close()
        try:
            proc = subprocess.run([PYTHON_EXECUTABLE, 'compression/options/'+filepath, f.name],
                                  capture_output=True, timeout=TIMEOUT, text=True, encoding='latin-1')
            if proc.returncode != 0:
                status_code = 500
                stderr = proc.stderr
                stdout = data
            else:
                status_code = 200
                stderr = proc.stderr
                stdout = proc.stdout
        except subprocess.TimeoutExpired:
            status_code = 501
            stderr = f"Tool timed out after {TIMEOUT} seconds."
            stdout = data
        except Exception as e:
            import traceback
            status_code = 502
            stderr = traceback.format_exc()
            stdout = data

    return dumps({"stderr": stderr, "stdout": stdout.removesuffix("\n\u001b[0m")}), status_code


@auth_required
@app.post("/tools/update")
def update_tools():
    if not os.path.isdir("compression"):
        os.system("git clone https://github.com/jailctf-merger-goog-golf/compression")
    try:
        proc = subprocess.run(['git', 'pull'],
                              capture_output=True, timeout=10.0, text=True, encoding='latin-1', cwd="compression")
        if proc.returncode != 0:
            status_code = 500
            output = proc.stderr
        else:
            status_code = 200
            output = proc.stdout
    except subprocess.TimeoutExpired:
        status_code = 501
        output = f"Clone timed out."
    except Exception as e:
        status_code = 502
        output = repr(e)

    return output, status_code


if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.run(host='0.0.0.0', port=5000)
