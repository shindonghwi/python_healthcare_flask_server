import librosa
import librosa.display
import soundfile


def load_librosa(audio_path, sample_rate=16000) -> dict:
    librosa_dict = {"y": None, "sr": None}
    try:
        y, sr = librosa.load(audio_path, sr=sample_rate)
        librosa_dict["y"] = y
        librosa_dict["sr"] = sr
    except:
        pass
    return librosa_dict


# def load_soundfile(audio_path, sample_rate=16000):
#     soundfile_dict = {"y": None, "sr": None}
#     try:
#         y, sr = soundfile.read(file=audio_path, samplerate=sample_rate)
#         soundfile_dict["y"] = y
#         soundfile_dict["sr"] = sr
#     except:
#         pass
#     return soundfile_dict
