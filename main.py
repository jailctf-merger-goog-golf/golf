from flask import Flask, render_template_string, url_for, send_from_directory, send_file, request
from flask import request
import subprocess
import os

app = Flask(__name__)


@app.route('/')
def home():
    return send_file("./index.html")


@app.route('/style.css')
def swag():
    return send_file("./style.css")


@app.route('/cm6.bundle.min.js')
def cm6():
    return send_file("./cm6.bundle.min.js", mimetype="application/javascript")


@app.route('/bundle.js')
def script():
    return send_file("./bundle.js", mimetype="application/javascript")


@app.route('/working/<path:filepath>')
def working(filepath):
    os.makedirs("working", exist_ok=True)
    return send_from_directory("./working/", filepath, mimetype='image/png')


@app.route('/legend.png')
def legend():
    return send_file("./legend.png", mimetype='image/png')


@app.post('/run/<int:task>')
def run(task):
    with open(f"./sols/task{task:03d}.py", 'w') as f:
        data = request.data.decode('latin-1')
        f.write(data)
    
    TIMEOUT = 10 # seconds
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


@app.get('/view/<int:task>')
def view(task):
    os.makedirs("working/view", exist_ok=True)
    if not os.path.isfile(f"./working/view/task{task:03d}.png"):
        subprocess.check_output(['python3', 'view-task.py', str(task)])
    return send_from_directory("./working/view/", f"task{task:03d}.png", mimetype='image/png')


@app.route('/sols/<int:task>')
def sols(task):
    return send_from_directory("./sols/", f"task{task:03d}.py", mimetype='application/x-python-code')


if __name__ == '__main__':
    app.run()
