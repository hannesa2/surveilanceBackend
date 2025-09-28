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


def toFileDescriptor(filename):
    states = os.stat(str(Path.cwd()) + "/" + UPLOAD_FOLDER + "/" + filename)
    return FileDescription(filename, states.st_size, states.st_mtime)


def toEncoder(file_description):
    return FileDescriptionEncoder().encode(file_description)


@app.route('/files', methods=['GET'])
def listFile():
    print("I do >/files<", request.method)
    if request.method == 'GET':
        files = os.listdir(UPLOAD_FOLDER)
        file_descriptors = sorted(list(map(toFileDescriptor, files)), key=operator.attrgetter('created'), reverse=True)
        encoded_file_descriptors = list(map(toEncoder, file_descriptors))
        return jsonify(results=encoded_file_descriptors)
    return ''


@app.route('/avi', methods=['GET'])
def listAvi():
    print("I do >/avi<", request.method)
    if request.method == 'GET':
        files = os.listdir(UPLOAD_FOLDER)
        listed = list(map(toFileDescriptor, files))
        filtered_listed = [s for s in listed if str(s.name).lower().endswith(".avi")]
        file_descriptors = sorted(filtered_listed, key=operator.attrgetter('created'), reverse=True)
        encoded_file_descriptors = list(map(toEncoder, file_descriptors))
        return jsonify(results=encoded_file_descriptors)
    return ''


@app.route('/movies/<filetype>', methods=['GET'])
def list_movies(filetype):
    print("I do >/movies/" + filetype + "<", request.method)
    if request.method == 'GET':
        files = os.listdir(UPLOAD_FOLDER)
        listed = list(map(toFileDescriptor, files))
        filtered_listed = [s for s in listed if str(s.name).lower().endswith(str(filetype).lower())]
        file_descriptors = sorted(filtered_listed, key=operator.attrgetter('created'), reverse=True)
        encoded_file_descriptors = list(map(toEncoder, file_descriptors))
        return jsonify(results=encoded_file_descriptors)
    return request.method + ' not supported'


@app.route('/deletemovie/<filetype>/<name>', methods=['GET'])
def delete_movie(filetype, name):
    print("I do >/deletemovie/" + filetype + "/" + name + "<", request.method)

    if os.path.exists(name):
        os.remove(name)
        print(f"File '{name}' deleted successfully.")
    else:
        print(f"File '{name}' not found.")

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
