from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory
import os
import yaml

from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = "files"
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

if os.path.isfile('parameter.yml'):
    with open('parameter.yml', 'r') as file:
        prime_service = yaml.safe_load(file)
        if __name__ == '__main__':
            UPLOAD_FOLDER = prime_service['file']['directory']


@app.route('/')
def index():
    return render_template('index.html', items=os.listdir(UPLOAD_FOLDER))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    print("I do a ", request.method)
    print("---headers---\r\n", request.headers)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            sub_url = ""
            if os.path.isfile('parameter.yml'):
                with open('parameter.yml', 'r') as file:
                    prime_service = yaml.safe_load(file)
                    if __name__ == '__main__':
                        sub_url = prime_service['server']['sub_url']
            print("sub_url=", sub_url)

            return redirect(sub_url + url_for('download_file', name=filename))
    return ''


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/get', methods=['GET'])
def get():
    name = request.args['name']
    try:
        fp = open(UPLOAD_FOLDER + '/' + name, 'r')
        content = fp.read()
        fp.close()
        return content
    except FileNotFoundError:
        print("Please check the path")


@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']

    fp = open(UPLOAD_FOLDER + '/' + name, 'w')
    fp.write('content of ' + name)
    fp.close()
    return redirect('/')


@app.route('/update', methods=['POST'])
def update():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    os.rename(UPLOAD_FOLDER + '/' + old_name, UPLOAD_FOLDER + '/' + new_name)
    return redirect('/')


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form['name']
    os.remove(UPLOAD_FOLDER + '/' + name)
    return redirect('/')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.secret_key = 'super secret key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 6000024
    items = os.listdir(UPLOAD_FOLDER)
    app.run(host="0.0.0.0", debug=True, port=5001)
