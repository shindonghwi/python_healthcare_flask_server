import librosa
import librosa.display
import matplotlib.pyplot as plt
import base64
from datetime import datetime
import numpy as np
import pyloudnorm as pyln


def save_loudness_image(soundfile_dict, save_folder_path):
    loudness_response = {}

    signal = soundfile_dict["y"]
    sample_rate = soundfile_dict["sr"]

    if sample_rate is None:
        sample_rate = 16000

    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, "librosa_loudness", current_timestamp)
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


def save_librosa_pitch(pitch_scores, save_folder_path):
    pitch_response = {}
    msg_list = []
    label = 'librosa_pitch'
    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, label, current_timestamp)
    f0_scores = np.array(pitch_scores)
    plt.figure(figsize=(20, 2))
    plt.plot(f0_scores)
    plt.xlabel(label)
    plt.savefig(upload_file_name)
    return create_spectrum_response(upload_file_name, pitch_response, msg_list), current_timestamp


def save_librosa_mfcc(mfcc_scores, save_folder_path):
    mfcc_response = {}
    msg_list = []
    label = 'librosa_mfcc'
    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, label, current_timestamp)
    mfcc = np.array(mfcc_scores).T
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(mfcc)
    plt.ylabel('MFCC coeffs')
    plt.xlabel('Time')
    plt.title(label)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(upload_file_name)
    return create_spectrum_response(upload_file_name, mfcc_response, msg_list), current_timestamp


def save_librosa_spectrogram(spectrogram_scores, save_folder_path):
    spectrogram_response = {}
    msg_list = []
    label = 'librosa_spectrogram'
    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, label, current_timestamp)
    spectrogram = np.array(spectrogram_scores).T
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(spectrogram)
    plt.ylabel('Frequency')
    plt.xlabel('Time')
    plt.title(upload_file_name)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(upload_file_name)
    return create_spectrum_response(upload_file_name, spectrogram_response, msg_list), current_timestamp


def save_librosa_mel_spectrogram(mel_scores, save_folder_path):
    mel_spectrogram_response = {}
    msg_list = []
    label = 'librosa_mel_spectrogram'
    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, label, current_timestamp)
    melspectrogram = np.array(mel_scores).T
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(melspectrogram)
    plt.ylabel('Frequency')
    plt.xlabel('Time')
    plt.title(label)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(upload_file_name)
    return create_spectrum_response(upload_file_name, mel_spectrogram_response, msg_list), current_timestamp


def save_librosa_spectral_centroid(spectral_centroid_scores, save_folder_path):
    centroid_response = {}
    msg_list = []
    label = 'librosa_spectral_centroid'
    current_timestamp = str(datetime.now().timestamp()).replace('.', '-')
    upload_file_name = '{}/{}_{}.png'.format(save_folder_path, label, current_timestamp)
    spectralcentriod = np.array(spectral_centroid_scores).squeeze()
    print(spectralcentriod.shape)
    plt.figure(figsize=(20, 2))
    plt.plot(spectralcentriod)
    plt.xlabel('Frames')
    plt.savefig(upload_file_name)
    return create_spectrum_response(upload_file_name, centroid_response, msg_list), current_timestamp
