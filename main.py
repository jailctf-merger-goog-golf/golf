from flask import Flask, send_from_directory, send_file, request, session, redirect
from flask import request
import subprocess
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


def auth_required(func):
    def wrapper(*args, **kwargs):
        if "auth" not in session or not session["auth"]:
            raise PermissionError('Unauthorized', 401)
        return func(*args, **kwargs)
    return wrapper


app = Flask(__name__)


def execute_task(task):
    TIMEOUT = 10  # seconds
    try:
        proc = subprocess.run(['python3', 'run-task.py', str(task)], capture_output=True, timeout=TIMEOUT, text=True)
        if proc.returncode != 0:
            status_code = 500
            output = proc.stderr
        else:
            status_code = 200
            output = proc.stdout
    except subprocess.TimeoutExpired:
        status_code = 501
        output = f"Code timed out after {TIMEOUT} seconds."
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
@app.route('/working/<path:filepath>')
def working(filepath):
    os.makedirs("working", exist_ok=True)
    return send_from_directory("./working/", filepath, mimetype='image/png')


@app.route('/legend.png')
def legend():
    return send_file("./legend.png", mimetype='image/png')


@auth_required
@app.post('/run/<int:task>')
def run(task):
    fpath = f"./sols/task{task:03d}.py"
    with open(fpath, 'wb') as f:
        data = request.data.replace(b'\x0d\x0a', b'\x0a')
        f.write(data)

    output, status_code = execute_task(task)
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
@app.get('/random')
def random_chal():
    ok = set(range(1,401))-{int(taskfile.removeprefix("task").removesuffix(".py")) for taskfile in os.listdir('./sols/')}
    if len(ok) == 0:
        return 'uhhhh all completed !?!?!?! good job future me', 500
    return str(choice(list(ok))), 200


if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.run(host='0.0.0.0', port=80)
