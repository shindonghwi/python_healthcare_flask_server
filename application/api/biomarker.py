from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.style as ms
import matplotlib
import base64
import pyloudnorm as pyln
import soundfile
import numpy as np

matplotlib.use('Agg')
ms.use('seaborn-muted')

route = 'biomarker'
biomarker = Blueprint('biomarker', __name__, url_prefix='/' + route)
biomarker.url_prefix = '/{}'.format(route)

ALLOWED_EXTENSIONS = {'aac', 'mp4', 'wav', 'm4a'}
save_folder = "{}/audio".format(os.getcwd())


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@biomarker.route('spectrum', methods=['POST'])
def extrack_audio_file():
    """
    오디오 파일을 받아서 mfcc, loudness bytearray를 반환하는 함수
    :parameter
        - (required) file: audio file
        - (optional) sample_rate, n_fft, n_mfcc, n_mels, hop_length, fmin, fmax, htk
    :return mfcc image bytearray
    """

    global save_folder

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
        resp = jsonify({'message': 'Allowed file types are aac, mp4, wav, m4a'})
        resp.status_code = 400

    if resp.status_code != 200:
        return resp

    file_full_name, file_name, file_ext = get_file_info(request.files['file'])

    mfcc_resp = load_mfcc(file_full_name, file_name)
    mel_resp = load_mel(file_full_name, file_name)
    loudness_resp = load_loudness(file_full_name, file_name)

    res = {}
    if mfcc_resp["status"] == 200 or loudness_resp["status"] == 200 or mel_resp["status"] == 200:
        res["status"] = 200
        res["msg"] = "success"
        os.remove("{}/{}.png".format(save_folder, file_name))
        os.remove("{}/{}.{}".format(save_folder, file_name, file_ext))
    else:
        if mfcc_resp["status"] == 200:
            res["status"] = loudness_resp["status"]
            res["msg"] = loudness_resp["msg"]
        elif mel_resp["status"] == 200:
            res["status"] = mfcc_resp["status"]
            res["msg"] = mfcc_resp["msg"]
        else:
            res["status"] = mel_resp["status"]
            res["msg"] = mel_resp["msg"]

    byte_dict = {}
    if mfcc_resp["status"] == 200:
        byte_dict["mfcc"] = mfcc_resp["bytes"]

    if loudness_resp["status"] == 200:
        byte_dict["loudness"] = loudness_resp["bytes"]

    if mel_resp["status"] == 200:
        byte_dict["mel"] = mel_resp["bytes"]

    res["data"] = byte_dict

    return jsonify(res)


def get_file_info(files):
    file_full_name = secure_filename(files.filename)
    file_name = file_full_name.split('.')[0]
    file_ext = file_full_name.split('.')[1]

    return file_full_name, file_name, file_ext


def load_mfcc(file_full_name, file_name):
    global save_folder

    mfcc_response = {}

    sample_rate = request.form.get('sample_rate', 16000)
    n_fft = request.form.get('n_fft', 512)
    n_mfcc = request.form.get('n_mfcc', 13)
    n_mels = request.form.get('n_mels', 40)
    hop_length = request.form.get('hop_length', 160)
    fmin = request.form.get('fmin', 0)
    fmax = request.form.get('fmax', None)
    htk = request.form.get('htk', False)

    try:
        y, sr = librosa.load("{}/{}".format(save_folder, file_full_name), sr=sample_rate, duration=5, offset=30)

        mfcc = librosa.feature.mfcc(y=y, sr=sample_rate, n_fft=n_fft,
                                    n_mfcc=n_mfcc, n_mels=n_mels,
                                    hop_length=hop_length,
                                    fmin=fmin, fmax=fmax, htk=htk)

        plt.figure(figsize=(18, 4))
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
            mfcc_response["status"] = 200
            mfcc_response["msg"] = "success"
            mfcc_response["bytes"] = str(base64_string)
        else:
            mfcc_response["status"] = 500
            mfcc_response["msg"] = "Audio File Extract Error"
    except Exception as e:
        mfcc_response["status"] = 400
        mfcc_response["msg"] = "Can\'t draw a spectrum : {}".format(e)

    return mfcc_response


def load_loudness(file_full_name, file_name):
    loudness_response = {}

    try:
        signal, sample_rate = soundfile.read("{}/{}".format(save_folder, file_full_name))

        meter = pyln.Meter(sample_rate)  # create BS.1770 meter
        chunks_size = int(meter.block_size * sample_rate)
        size = len(signal)
        shift = int(0.025 * sample_rate)

        loudness = []
        s = 0
        while True:
            if s + chunks_size > size: break
            loudness.append(meter.integrated_loudness(signal[s:s + chunks_size]))
            s += shift

        plt.figure(figsize=(18, 4))
        plt.plot(loudness)
        plt.xlabel('Frames')
        save_file_name = '{}/{}.png'.format(save_folder, file_name)
        plt.savefig(save_file_name)

        with open(save_file_name, 'rb') as img:
            base64_string = base64.b64encode(img.read())

        if base64_string is not None:
            loudness_response["status"] = 200
            loudness_response["msg"] = "success"
            loudness_response["bytes"] = str(base64_string)
        else:
            loudness_response["status"] = 500
            loudness_response["msg"] = "Audio File Extract Error"
    except Exception as e:
        loudness_response["status"] = 400
        loudness_response["msg"] = "Can\'t draw a spectrum : {}".format(e)

    return loudness_response


def load_mel(file_full_name, file_name):
    global save_folder

    mel_response = {}

    sample_rate = request.form.get('sample_rate', 16000)
    input_stride = int(round(sample_rate* 0.010))

    try:
        y, sr = librosa.load("{}/{}".format(save_folder, file_full_name), sr=sample_rate, duration=5, offset=30)
        S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)

        plt.figure(figsize=(18, 4))
        librosa.display.specshow(librosa.power_to_db(S, ref=np.max), y_axis='mel', sr=sr, hop_length=input_stride, x_axis='time')
        plt.title('mel power spectrogram')
        plt.colorbar(format='%+02.0f dB')
        plt.tight_layout()
        save_file_name = '{}/{}.png'.format(save_folder, file_name)
        plt.savefig(save_file_name)

        with open(save_file_name, 'rb') as img:
            base64_string = base64.b64encode(img.read())

        if base64_string is not None:
            mel_response["status"] = 200
            mel_response["msg"] = "success"
            mel_response["bytes"] = str(base64_string)
        else:
            mel_response["status"] = 500
            mel_response["msg"] = "Audio File Extract Error"
    except Exception as e:
        mel_response["status"] = 400
        mel_response["msg"] = "Can\'t draw a spectrum : {}".format(e)

    return mel_response

