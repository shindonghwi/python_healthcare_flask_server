from flask import Blueprint, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.style as ms
import matplotlib
import base64
from application.api import check_file

matplotlib.use('Agg')
ms.use('seaborn-muted')

route = 'biomarker'
biomarker = Blueprint(route, __name__)
biomarker.url_prefix = '/{}'.format(route)

ALLOWED_EXTENSIONS = {'aac', 'mp4', 'wav'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@biomarker.route('/mfcc', methods=['POST'])
def extrack_mfcc_image():
    """
    오디오 파일을 받아서 mfcc bytearray를 반환하는 함수
    :parameter
        - (required) file: audio file
        - (optional) sample_rate, n_fft, n_mfcc, n_mels, hop_length, fmin, fmax, htk
    :return mfcc image bytearray
    """
    save_folder = "{}/audio".format(os.getcwd())

    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
    if file and allowed_file(file.filename):
        file.save("{}/{}".format(save_folder, secure_filename(file.filename)))
        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 200
    else:
        resp = jsonify({'message': 'Allowed file types are aac, mp4, wav'})
        resp.status_code = 400

    sample_rate = request.form.get('sample_rate', 16000)
    n_fft = request.form.get('n_fft', 512)
    n_mfcc = request.form.get('n_mfcc', 13)
    n_mels = request.form.get('n_mels', 40)
    hop_length = request.form.get('hop_length', 160)
    fmin = request.form.get('fmin', 0)
    fmax = request.form.get('fmax', None)
    htk = request.form.get('htk', False)

    if resp.status_code != 200:
        return resp

    file_full_name = secure_filename(request.files['file'].filename)
    file_name = file_full_name.split('.')[0]
    file_ext = file_full_name.split('.')[1]

    y, sr = librosa.load("{}/{}".format(save_folder, file_full_name), sr=sample_rate, duration=5, offset=30)

    try:
        mfcc = librosa.feature.mfcc(y=y, sr=sample_rate, n_fft=n_fft,
                                    n_mfcc=n_mfcc, n_mels=n_mels,
                                    hop_length=hop_length,
                                    fmin=fmin, fmax=fmax, htk=htk)

        plt.figure(figsize=(12, 4))
        librosa.display.specshow(mfcc)
        plt.ylabel('MFCC coeffs')
        plt.xlabel('Time')
        plt.title('MFCC')
        plt.colorbar()
        plt.tight_layout()
        save_file_name = '{}/{}.png'.format(save_folder, file_name)
        plt.savefig(save_file_name)

        with open(save_file_name, 'rb') as img:
            base64_string = base64.b64encode(img.read())

        if base64_string is not None:
            resp = jsonify({'message': 'success', 'data': str(base64_string)})
            resp.status_code = 200
            os.remove("{}/{}.png".format(save_folder, file_name))
            os.remove("{}/{}.{}".format(save_folder, file_name, file_ext))
        else:
            resp = jsonify({'message': 'Audio File Extract Error'})
            resp.status_code = 500
    except:
        resp = jsonify({'message': 'Can\'t draw a spectrum'})
        resp.status_code = 204

    return resp

