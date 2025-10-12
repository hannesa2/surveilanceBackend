import io
import os
import subprocess

import yaml
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file

import tools
from logfile import logfile_name, reverse_readline
from tools import withWebCam

app = Flask(__name__, template_folder='templates')

if os.path.isfile('parameter.yml'):
    with open('parameter.yml', 'r') as file:
        prime_service = yaml.safe_load(file)
        if __name__ == '__main__':
            tools.UPLOAD_FOLDER = prime_service['file']['directory']
            print("Use from parameter.yml tools.UPLOAD_FOLDER=" + tools.UPLOAD_FOLDER)


@app.route('/')
def index():
    print("I do >index<")
    return render_template('index.html', items=os.listdir(tools.UPLOAD_FOLDER))


def absolute_file_paths(directory):
    path = os.path.abspath(directory)
    return [entry.path for entry in os.scandir(path) if entry.is_file()]


@app.route('/version')
def version():
    execute_path = os.path.dirname(__file__)
    try:
        return subprocess.check_output(['git', 'describe', '--tags'], cwd=execute_path).decode('ascii').strip()
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        where = "undefined"
        pwd = "undefined"
        whoami = "undefined"
        try:
            whoami = subprocess.check_output(['whoami']).decode('ascii').strip()
            pwd = subprocess.check_output(['pwd']).decode('ascii').strip()
            where = subprocess.check_output(['whereis', 'git']).decode('ascii').strip()
        except Exception as e_where:
            jsonify({'error exception': str(e)}, {'whereis git': str(e_where)}, {'execute_path': str(execute_path)}, {'pwd': str(pwd)},
                    {'whoami': str(whoami)}), 500
        return jsonify({'error': str(e)}, {'whereis git': str(where)}, {'execute_path': str(execute_path)}, {'pwd': str(pwd)}, {'whoami': str(whoami)}), 500


@app.route('/files/<webcam>', methods=['GET'])
def listFile(webcam):
    print("I do >/files/" + webcam + "<", request.method)
    if request.method == 'GET':
        # Validate path exists and is a directory
        if not os.path.exists(tools.UPLOAD_FOLDER + "/" + webcam):
            return jsonify({'error': 'Path does not exist ' + tools.UPLOAD_FOLDER + "/" + webcam}), 404

        if not os.path.isdir(tools.UPLOAD_FOLDER + "/" + webcam):
            return jsonify({'error': 'Path is not a directory ' + tools.UPLOAD_FOLDER + "/" + webcam}), 400

        files_info = []
        # for item in absolute_file_paths(tools.UPLOAD_FOLDER + "/" + webcam):
        for item in os.listdir(tools.UPLOAD_FOLDER + "/" + webcam):
            item_path = os.path.join(tools.UPLOAD_FOLDER + "/" + webcam, item)

            stats = os.stat(item_path)

            file_info = {
                'name': item,
                'webcam': webcam,
                'size': stats.st_size,
                'size_readable': format_size(stats.st_size),
                'created': stats.st_ctime,
            }

            files_info.append(file_info)

        # Sort by filename
        files_info.sort(key=lambda x: x['created'])

        return jsonify(files_info), 200
    return ''


@app.route('/avi/<webcam>', methods=['GET'])
def listAvi(webcam):
    print("I do >/avi/" + webcam + "<", request.method)
    if request.method == 'GET':
        return list_movies("avi", webcam)
    return ''


@app.route('/movies/<webcam>/<filetype>', methods=['GET'])
def list_movies(filetype, webcam):
    print("I do >/movies/" + filetype + "/" + webcam + "<", request.method)
    extensions_simple = [ext.strip().lower() for ext in filetype.split(',')]
    extensions = [f"{'.'}{s}" for s in extensions_simple]  # add a leading '.'

    if request.method == 'GET':
        # Validate path exists and is a directory
        if not os.path.exists(tools.UPLOAD_FOLDER + "/" + webcam):
            return jsonify({'error': 'Path does not exist ' + tools.UPLOAD_FOLDER + "/" + webcam}), 404

        if not os.path.isdir(tools.UPLOAD_FOLDER + "/" + webcam):
            return jsonify({'error': 'Path is not a directory ' + tools.UPLOAD_FOLDER + "/" + webcam}), 400

        files_info = []
        # for item in absolute_file_paths(tools.UPLOAD_FOLDER + "/" + webcam):
        for item in os.listdir(tools.UPLOAD_FOLDER + "/" + webcam):
            _, file_ext = os.path.splitext(item)
            # Include files matching extension
            if file_ext.lower() not in extensions:
                continue

            item_path = os.path.join(tools.UPLOAD_FOLDER + "/" + webcam, item)

            stats = os.stat(item_path)

            file_info = {
                'name': item,
                'webcam': webcam,
                'size': stats.st_size,
                'size_readable': format_size(stats.st_size),
                'created': stats.st_ctime,
            }

            files_info.append(file_info)

        # Sort by filename
        files_info.sort(key=lambda x: x['created'])

        return jsonify(files_info), 200
    return None


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
    return jsonify(reverse_readline(filename=withWebCam(logfile_name, webcam), count=int(count))), 200


@app.route('/logpage/<webcam>/<count>/<skip>', methods=['GET'])
def log_pagination(webcam, count, skip):
    print("I do >/logpage/" + webcam + "/" + count + "/" + skip + "<", request.method)
    return jsonify(reverse_readline(filename=withWebCam(logfile_name, webcam),
                                    skip_last=int(skip),
                                    count=int(count))), 200


@app.route('/brightness/<webcam>/<count>/<skip>', methods=['GET'])
def brightness(webcam, count, skip):
    print("I do >/brightness/" + webcam + "/" + count + "/" + skip + "<", request.method)
    return jsonify(reverse_readline(filename=withWebCam(logfile_name, webcam),
                                    skip_last=int(skip),
                                    search_string="Brightness",
                                    count=int(count))), 200


@app.route('/files4movie/<webcam>/<moviename>', methods=['GET'])
def files4movie(webcam, movie_name):
    print("I do >/files4movie/" + webcam + "/" + movie_name + "<", request.method)
    # Validate path exists and is a directory
    if not os.path.exists(tools.UPLOAD_FOLDER + "/" + webcam):
        return jsonify({'error': 'Path does not exist ' + tools.UPLOAD_FOLDER + "/" + webcam}), 404

    if not os.path.isdir(tools.UPLOAD_FOLDER + "/" + webcam):
        return jsonify({'error': 'Path is not a directory ' + tools.UPLOAD_FOLDER + "/" + webcam}), 400

    files_info = []
    extensions = ['.jpg']
    filter_movie_name = str(movie_name).split("/", 1)[0][0:11].lower()
    # for item in absolute_file_paths(tools.UPLOAD_FOLDER + "/" + webcam):
    for item in os.listdir(tools.UPLOAD_FOLDER + "/" + webcam):
        _, file_ext = os.path.splitext(item)
        # Include files matching extension
        if file_ext.lower() not in extensions:
            continue

        if item.find(filter_movie_name) == -1:
            continue

        item_path = os.path.join(tools.UPLOAD_FOLDER + "/" + webcam, item)

        stats = os.stat(item_path)

        file_info = {
            'name': item,
            'webcam': webcam,
            'size': stats.st_size,
            'size_readable': format_size(stats.st_size),
            'created': stats.st_ctime,
        }

        files_info.append(file_info)

    # Sort by filename
    files_info.sort(key=lambda x: x['created'])

    return jsonify(files_info), 200


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
def pictures(webcam, size, _id):
    print("I do >/pictures/" + webcam + "/" + size + "/" + _id + "<", request.method)
    return "pictures as bitmap not implemented"  # TODO


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


def format_size(bytes_given):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_given < 1024.0:
            return f"{bytes_given:.2f} {unit}"
        bytes_given /= 1024.0
    return f"{bytes_given:.2f} PB"


if __name__ == '__main__':
    print("tools.UPLOAD_FOLDER=" + tools.UPLOAD_FOLDER)
    # print("tools.UPLOAD_FOLDER=" + str(Path.cwd()) + "/" + tools.UPLOAD_FOLDER)
    if not os.path.exists(tools.UPLOAD_FOLDER):
        os.makedirs(tools.UPLOAD_FOLDER)

    app.secret_key = 'super secret key'
    app.config['tools.UPLOAD_FOLDER'] = tools.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 6000024
    items = os.listdir(tools.UPLOAD_FOLDER)
    app.run(host="0.0.0.0", debug=True, port=5001)
