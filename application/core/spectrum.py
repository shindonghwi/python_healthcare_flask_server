from flask import request
import librosa
import librosa.display
import matplotlib.pyplot as plt
import base64
from datetime import datetime
import numpy as np
import pyloudnorm as pyln


def save_mfcc_image(librosa_dict, save_folder_path):
    mfcc_response = {}

    signal = librosa_dict["y"]
    sample_rate = librosa_dict["sr"]

    if sample_rate is None:
        sample_rate = 16000

    n_fft = request.form.get('n_fft', 512)
    n_mfcc = request.form.get('n_mfcc', 13)
    n_mels = request.form.get('n_mels', 40)
    hop_length = request.form.get('hop_length', 160)
    fmin = request.form.get('fmin', 0)
    fmax = request.form.get('fmax', None)
    htk = request.form.get('htk', False)

    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, "mfcc", current_timestamp)

    msg_list = []

    try:
        mfcc = librosa.feature.mfcc(
            y=signal, sr=sample_rate, n_fft=n_fft,
            n_mfcc=n_mfcc, n_mels=n_mels, hop_length=hop_length,
            fmin=fmin, fmax=fmax, htk=htk
        )

        plt.figure(figsize=(18, 4))
        librosa.display.specshow(mfcc)
        plt.ylabel('MFCC coeffs')
        plt.xlabel('Time')
        plt.title('MFCC')
        plt.colorbar(format='%+02.0f dB')
        plt.savefig(upload_file_name)
    except Exception as e:
        mfcc_response["status"] = 404
        msg_list.append("MFCC Feature Extract Fail : {}".format(e))

    return create_spectrum_response(upload_file_name, mfcc_response, msg_list), current_timestamp


def save_mel_image(librosa_dict, save_folder_path):
    mel_response = {}

    signal = librosa_dict["y"]
    sample_rate = librosa_dict["sr"]
    n_mels = 40

    if sample_rate is None:
        sample_rate = 16000

    input_nfft = int(round(sample_rate * 0.025))
    input_stride = int(round(sample_rate * 0.010))

    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, "mel", current_timestamp)

    msg_list = []

    try:
        S = librosa.feature.melspectrogram(signal, n_mels=n_mels, hop_length=input_stride, n_fft=input_nfft)
        plt.figure(figsize=(18, 4))
        librosa.display.specshow(librosa.power_to_db(S, ref=np.max), y_axis='mel', sr=sample_rate,
                                 hop_length=input_stride,
                                 x_axis='time')
        plt.title('mel power spectrogram')
        plt.colorbar(format='%+02.0f dB')
        plt.savefig(upload_file_name)
    except Exception as e:
        mel_response["status"] = 404
        msg_list.append("Mel Feature Extract Fail : {}".format(e))

    return create_spectrum_response(upload_file_name, mel_response, msg_list), current_timestamp


def save_loudness_image(soundfile_dict, save_folder_path):
    loudness_response = {}

    signal = soundfile_dict["y"]
    sample_rate = soundfile_dict["sr"]

    if sample_rate is None:
        sample_rate = 16000

    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, "loudness", current_timestamp)
    msg_list = []

    try:
        meter = pyln.Meter(sample_rate)
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
        plt.savefig(upload_file_name)
    except Exception as e:
        loudness_response["status"] = 404
        msg_list.append("Loudness Feature Extract Fail : {}".format(e))

    return create_spectrum_response(upload_file_name, loudness_response, msg_list), current_timestamp


def create_spectrum_response(upload_file_name, res, msg_list):
    try:
        with open(upload_file_name, 'rb') as img:
            base64_string = base64.b64encode(img.read())

        if base64_string is not None:
            res["status"] = 200
            res["bytes"] = str(base64_string)
            msg_list.append("success")
        else:
            res["status"] = 500
            msg_list.append("Uploaded Audio File Read Error")
    except Exception as e:
        res["status"] = 404
        msg_list.append("Can\'t draw a spectrum : {}".format(e))

        res["msg"] = msg_list
    return res
