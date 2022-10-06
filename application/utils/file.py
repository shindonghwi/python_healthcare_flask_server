from werkzeug.utils import secure_filename
import os

AUDIO_ALLOWED_EXTENSIONS = {'aac', 'mp4', 'wav', 'm4a'}
FEATS_ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename, type) -> bool:
    if type == "audio":
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in AUDIO_ALLOWED_EXTENSIONS
    else:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FEATS_ALLOWED_EXTENSIONS


def check_file_upload(req_files, save_folder) -> dict:
    upload_response = {}

    audio_file = req_files.get("audio", None)
    feats_file = req_files.get("feats", None)

    if audio_file:
        if allowed_file(audio_file.filename, type="audio"):
            audio_file.save("{}/{}".format(save_folder, secure_filename(audio_file.filename)))
            upload_response["status"] = 200
            upload_response["msg"] = 'File successfully uploaded'
        else:
            upload_response["status"] = 400
            upload_response["msg"] = 'Allowed Audio file types are {}'.format(AUDIO_ALLOWED_EXTENSIONS)
            return upload_response
    else:
        upload_response["status"] = 400
        upload_response["msg"] = 'not found params -> `audio` type: {}'.format(AUDIO_ALLOWED_EXTENSIONS)
        return upload_response

    if feats_file:
        if allowed_file(feats_file.filename, type="feats"):
            feats_file.save("{}/{}".format(save_folder, secure_filename(feats_file.filename)))
            upload_response["status"] = 200
            upload_response["msg"] = 'File successfully uploaded'
        else:
            upload_response["status"] = 400
            upload_response["msg"] = 'Allowed Feats file types are {}'.format(FEATS_ALLOWED_EXTENSIONS)
            return upload_response
    else:
        upload_response["status"] = 400
        upload_response["msg"] = 'not found params -> `feats` / type: {}'.format(FEATS_ALLOWED_EXTENSIONS)
        return upload_response

    return upload_response


def get_file_info(files):
    return {
        "full_name": secure_filename(files.filename),
        "name": secure_filename(files.filename).split('.')[0],
        "ext": secure_filename(files.filename).split('.')[1]
    }


def remove_uploaded_file(spectrum_list, save_folder, file_info):
    for spectrum_name, timestamp in spectrum_list.items():
        try:
            os.remove("{}/{}_{}.png".format(save_folder, spectrum_name, timestamp))
        except Exception as e:
            print(e, spectrum_name)
    try:
        os.remove("{}/{}.{}".format(save_folder, file_info["name"], file_info["ext"]))
    except Exception as e:
        print(e, spectrum_name)
