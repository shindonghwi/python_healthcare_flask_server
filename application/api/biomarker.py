from flask import Blueprint, request
import os
import matplotlib.style as ms
import matplotlib
from application.utils.file import check_file_upload, get_file_info, remove_uploaded_file
from application.utils.audio import load_librosa, load_soundfile
from application.core.spectrum import save_mfcc_image, save_mel_image, save_loudness_image
import time
matplotlib.use('Agg')
ms.use('seaborn-muted')

route = 'biomarker'
biomarker = Blueprint('biomarker', __name__, url_prefix='/' + route)
biomarker.url_prefix = '/{}'.format(route)

save_folder = "{}/audio".format(os.getcwd())


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
    start = time.time()

    # 사용 가능한 파일인지 확인한다.
    file_resp = check_file_upload(request.files, save_folder)
    if file_resp["status"] != 200:
        return file_resp
    file_info = get_file_info(request.files['file'])

    # load librosa
    librosa_dict = load_librosa(audio_path="{}/{}".format(save_folder, file_info["full_name"]))
    soundfile_dict = load_soundfile(audio_path="{}/{}".format(save_folder, file_info["full_name"]))

    # save spectrum image
    mfcc_resp, mfcc_uploaded_timestamp = save_mfcc_image(librosa_dict=librosa_dict, save_folder_path=save_folder)
    mel_resp, mel_uploaded_timestamp = save_mel_image(librosa_dict=librosa_dict, save_folder_path=save_folder)
    loudness_resp, loudness_uploaded_timestamp = save_loudness_image(soundfile_dict=soundfile_dict,
                                                                     save_folder_path=save_folder)

    # remove sepctrum image, audo
    spectrum_list = {
        "mfcc": mfcc_uploaded_timestamp,
        "mel": mel_uploaded_timestamp,
        "loudness": loudness_uploaded_timestamp,
    }
    remove_uploaded_file(spectrum_list, save_folder, file_info)

    response = {}

    if mfcc_resp["status"] != 200 or mel_resp["status"] != 200 or loudness_resp["status"] != 200:
        response["status"] = 404
        response["msg"] = "No Spectrum Data"
        response["data"] = None
    else:
        response["status"] = 200
        response["msg"] = "success"
        response["data"] = {
            "mfcc": mfcc_resp,
            "mel": mel_resp,
            "loudness": loudness_resp,
        }

    response["execution_time"] = time.time() - start
    return response

