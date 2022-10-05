from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'aac', 'mp4', 'wav'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_file(request_file, save_folder):
    response = None
    try:
        if 'file' not in request_file:
            response = jsonify({'message': 'No file part in the request'})
            response.status_code = 400
        file = request_file['file']
        if file.filename == '':
            response = jsonify({'message': 'No file selected for uploading'})
            response.status_code = 400
        if file and allowed_file(file.filename):
            file.save("{}/{}".format(save_folder, secure_filename(file.filename)))
            response = jsonify({'message': 'File successfully uploaded'})
            response.status_code = 200
        else:
            response = jsonify({'message': 'Allowed file types are aac, mp4, wav'})
            response.status_code = 400
    except:
        pass
    finally:
        return response
