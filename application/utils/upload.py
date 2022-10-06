from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'aac', 'mp4', 'wav', 'm4a'}


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_file_upload(req_files, save_folder) -> dict:
    upload_response = {}
    if 'file' not in req_files:
        upload_response["status"] = 400
        upload_response["msg"] = 'No file part in the request'
    file = req_files['file']
    if file.filename == '':
        upload_response["status"] = 400
        upload_response["msg"] = 'No file selected for uploading'
    if file and allowed_file(file.filename):
        file.save("{}/{}".format(save_folder, secure_filename(file.filename)))
        upload_response["status"] = 200
        upload_response["msg"] = 'File successfully uploaded'
    else:
        upload_response["status"] = 400
        upload_response["msg"] = 'Allowed file types are {}'.format(ALLOWED_EXTENSIONS)

    return upload_response
