import io
import operator
import os
import subprocess

import yaml
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file

from fileDescription import FileDescription, FileDescriptionEncoder

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = "./files"

if os.path.isfile('parameter.yml'):
    with open('parameter.yml', 'r') as file:
        prime_service = yaml.safe_load(file)
        if __name__ == '__main__':
            UPLOAD_FOLDER = prime_service['file']['directory']
            print("Use from parameter.yml UPLOAD_FOLDER=" + UPLOAD_FOLDER)


@app.route('/')
def index():
    print("I do >index<")
    return render_template('index.html', items=os.listdir(UPLOAD_FOLDER))


def withWebCam(filename, webcam_name):
    return UPLOAD_FOLDER + "/" + webcam_name + "/" + filename


def toFileDescriptor(absolute_filename):
    states = os.stat(absolute_filename)
    web_cam = str(absolute_filename).split('/')[-2]
    file_name = str(absolute_filename).split('/')[-1]
    return FileDescription(file_name, web_cam, states.st_size, states.st_mtime)


def toEncoder(file_description):
    return FileDescriptionEncoder().encode(file_description)


def absolute_file_paths(directory):
    path = os.path.abspath(directory)
    return [entry.path for entry in os.scandir(path) if entry.is_file()]


@app.route('/version')
def version():
    return subprocess.check_output(['git', 'describe', '--tags']).decode('ascii').strip()


@app.route('/files/<webcam>', methods=['GET'])
def listFile(webcam):
    print("I do >/files/" + webcam + "<", request.method)
    if request.method == 'GET':
        files = absolute_file_paths(UPLOAD_FOLDER + "/" + webcam)
        file_descriptors = sorted(list(map(toFileDescriptor, files)), key=operator.attrgetter('created'), reverse=True)
        encoded_file_descriptors = list(map(toEncoder, file_descriptors))
        return jsonify(results=encoded_file_descriptors)
    return ''


@app.route('/avi/<webcam>', methods=['GET'])
def listAvi(webcam):
    print("I do >/avi/" + webcam + "<", request.method)
    if request.method == 'GET':
        files = absolute_file_paths(UPLOAD_FOLDER + "/" + webcam)
        listed = list(map(toFileDescriptor, files))
        filtered_listed = [s for s in listed if str(s.name).lower().endswith(".avi")]
        file_descriptors = sorted(filtered_listed, key=operator.attrgetter('created'), reverse=True)
        encoded_file_descriptors = list(map(toEncoder, file_descriptors))
        return jsonify(results=encoded_file_descriptors)
    return ''


@app.route('/movies/<filetype>/<webcam>', methods=['GET'])
def list_movies(filetype, webcam):
    print("I do >/movies/" + filetype + "," + webcam + "<", request.method)
    if request.method == 'GET':
        files = absolute_file_paths(UPLOAD_FOLDER + "/" + webcam)
        listed = list(map(toFileDescriptor, files))
        filtered_listed = [s for s in listed if str(s.name).lower().endswith(str(filetype).lower())]
        file_descriptors = sorted(filtered_listed, key=operator.attrgetter('created'), reverse=True)
        encoded_file_descriptors = list(map(toEncoder, file_descriptors))
        return jsonify(results=encoded_file_descriptors)
    return request.method + ' not supported'


@app.route('/deletemovie/<webcam>/<filetype>/<name>', methods=['GET'])
def delete_movie(webcam, filetype, name):
    print("I do >/deletemovie/" + webcam + "/" + filetype + "/" + name + "<", request.method)
    complete_name = webcam + "/" + name
    if os.path.exists(complete_name):
        os.remove(complete_name)
        print(f"File '{complete_name}' deleted successfully.")
    else:
        print(f"File '{complete_name}' not found.")

    return list_movies(filetype)


@app.route('/log/<webcam>/<count>', methods=['GET'])
def log(webcam, count):
    print("I do >/log/" + webcam + "/" + count + "<", request.method)
    return "log not implemented"  # TODO


@app.route('/logpage/<webcam>/<count>/<skip>', methods=['GET'])
def logpage(webcam, count, skip):
    print("I do >/logpage/" + webcam + "/" + count + "/" + skip + "<", request.method)
    return "logpage not implemented"  # TODO


@app.route('/brightness/<webcam>/<count>/<skip>', methods=['GET'])
def brightness(webcam, count, skip):
    print("I do >/brightness/" + webcam + "/" + count + "/" + skip + "<", request.method)
    return "brightness not implemented"  # TODO


@app.route('/files4movie/<webcam>/<moviename>', methods=['GET'])
def files4movie(webcam, moviename):
    print("I do >/files4movie/" + webcam + "/" + moviename + "<", request.method)
    filter = str(moviename).split("/", 1)[0][0:11].lower()
    files = absolute_file_paths(UPLOAD_FOLDER + "/" + webcam)
    listed = list(map(toFileDescriptor, files))
    filtered_listed = [s for s in listed if str(s.name).lower().endswith(str(".jpg").lower()) and str(s.name).lower().find(filter) > 0]
    encoded_file_descriptors = list(map(toEncoder, filtered_listed))
    return jsonify(results=encoded_file_descriptors)


@app.route('/reload/<webcam>', methods=['GET'])
def reload(webcam):
    print("I do >/reload/" + webcam + "<", request.method)
    return "reload not implemented"  # TODO


@app.route('/restart/<webcam>', methods=['GET'])
def restart(webcam):
    print("I do >/restart/" + webcam + "<", request.method)
    return "restart not implemented"  # TODO


# Streaming
@app.route('/img/<webcam>/<size>/<name>', methods=['GET'])
def imgSize(webcam, size, name):
    print("I do >/img/" + webcam + "/" + size + "/" + name + "<", request.method)
    image = Image.open(withWebCam(name, webcam))
    image.thumbnail((int(size), int(size)))
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG', quality=90)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/movie/<webcam>/<name>', methods=['GET'])
def movie(webcam, name):
    print("I do >/movie/" + webcam + name + "<", request.method)
    return send_file(withWebCam(name, webcam), mimetype='image/gif')


@app.route('/pictures/img/<webcam>/<size>/<id>', methods=['GET'])
def pictures(webcam, size, id):
    print("I do >/pictures/" + webcam + "/" + size + "/" + id + "<", request.method)
    return "pictures as bitmap not implemented"  # TODO


if __name__ == '__main__':
    print("UPLOAD_FOLDER=" + UPLOAD_FOLDER)
    # print("UPLOAD_FOLDER=" + str(Path.cwd()) + "/" + UPLOAD_FOLDER)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.secret_key = 'super secret key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 6000024
    items = os.listdir(UPLOAD_FOLDER)
    app.run(host="0.0.0.0", debug=True, port=5001)
