from flask import Blueprint, request
import os
import matplotlib.style as ms
import matplotlib
from application.utils.file import check_file_upload, get_file_info, remove_uploaded_file
from application.utils.audio import load_librosa
from application.core.spectrum import *
import time
import json

matplotlib.use('Agg')
ms.use('seaborn-muted')

route = 'biomarker'
biomarker = Blueprint('biomarker', __name__, url_prefix='/' + route)
biomarker.url_prefix = '/{}'.format(route)

save_folder = "{}/audio".format(os.getcwd())


@biomarker.route('spectrum', methods=['POST'])
def extrack_audio_file():
    """
    오디오 파일을 받아서 이미지 bytearray를 반환하는 함수

    audio file -> Waveform & Spectrogram, (완료)Loudness
    json file  -> (완료)Pitch, (완료)Mfcc, (완료)Spectrogram, (완료)MelSpectrogram, Speech Activity Detection, (완료)SpectralCentroid

    :parameter
        - (required) file: audio file
        - (optional) sample_rate, n_fft, n_mfcc, n_mels, hop_length, fmin, fmax, htk
    :return mfcc image bytearray
    """

    global save_folder
    start = time.time()
    response = {
        "status": None,
        "msg": None,
        "data": {}
    }

    # 사용 가능한 파일인지 확인한다.
    file_resp = check_file_upload(request.files, save_folder)
    if file_resp["status"] == 200:

        audio_file_info = get_file_info(request.files['audio'])
        feats_file_info = get_file_info(request.files['feats'])

        if feats_file_info["length"] > 100000:
            response["status"] = 510
            response["msg"] = "(Not Extend) - Too Large Json File .."
            return response

        # audio 파일에서 그래프 추출
        librosa_dict = load_librosa(audio_path="{}/{}".format(save_folder, audio_file_info["full_name"]))
        loudness_resp, loudness_uploaded_ts = save_loudness_image(librosa_dict, save_folder)
        response["data"]['librosa_loudness'] = loudness_resp

        remove_list = {"librosa_loudness": loudness_uploaded_ts}
        remove_uploaded_file(remove_list, save_folder, audio_file_info)

        # json 파일에서 그래프 추출
        feats_file = open("{}/{}".format(save_folder, feats_file_info["full_name"]))
        try:
            feats = json.load(feats_file)
        except Exception as e:
            response["status"] = 500
            response["msg"] = "Too Large Json File .. : {}".format(e)
            return response

        if feats.get('acoustic') is not None:
            pitch_resp, pitch_ts = save_librosa_pitch(feats['acoustic']['LibrosaPitch'], save_folder)
            mfcc_resp, mfcc_ts = save_librosa_mfcc(feats['acoustic']['LibrosaMFCC'], save_folder)
            spectrogram_resp, spectrogram_ts = save_librosa_spectrogram(feats['acoustic']['LibrosaSpectrogram'], save_folder)
            mel_spectrogram_resp, mel_spectrogram_ts = save_librosa_mel_spectrogram(feats['acoustic']['LibrosaMelSpectrogram'], save_folder)
            centroid_resp, centroid_ts = save_librosa_spectral_centroid(feats['acoustic']['LibrosaSpectralCentroid'], save_folder)

            remove_list = {
                "librosa_pitch": pitch_ts,
                "librosa_mfcc": mfcc_ts,
                "librosa_spectrogram": spectrogram_ts,
                "librosa_mel_spectrogram": mel_spectrogram_ts,
                "librosa_spectral_centroid": centroid_ts,
            }

            remove_uploaded_file(remove_list, save_folder, feats_file_info)

            response["data"]['librosa_pitch'] = pitch_resp
            response["data"]['librosa_mfcc'] = mfcc_resp
            response["data"]['librosa_spectrogram'] = spectrogram_resp
            response["data"]['librosa_mel_spectrogram'] = mel_spectrogram_resp
            response["data"]['librosa_spectral_centroid'] = centroid_resp

        if response['data'] is None:
            response["status"] = 404
            response["msg"] = 'No Spectrum Data'
        else:
            response["status"] = 200
            response["msg"] = 'success'
    else:
        return file_resp

    response["execution_time"] = time.time() - start
    feats_file.close()
    return response
