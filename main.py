import operator
import os
from pathlib import Path

import yaml
from flask import Flask, render_template, request, jsonify

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
    return webcam_name + "/" + filename


def toFileDescriptor(absolute_filename):
    states = os.stat(absolute_filename)
    web_cam = str(absolute_filename).split('/')[-2]
    file_name = str(absolute_filename).split('/')[-1]
    return FileDescription(web_cam + "/" + file_name, states.st_size, states.st_mtime)


def toEncoder(file_description):
    return FileDescriptionEncoder().encode(file_description)


def absolute_file_paths(directory):
    path = os.path.abspath(directory)
    return [entry.path for entry in os.scandir(path) if entry.is_file()]


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
