import librosa
import librosa.display
import soundfile


def load_librosa(audio_path, sample_rate=16000) -> dict:
    librosa_dict = {"y": None, "sr": None}
    try:
        y, sr = librosa.load(audio_path, sr=sample_rate, duration=5, offset=30)
        librosa_dict["y"] = y
        librosa_dict["sr"] = sr
    except:
        pass
    return librosa_dict


def load_soundfile(audio_path):
    soundfile_dict = {"y": None, "sr": None}
    try:
        y, sr = soundfile.read(audio_path)
        soundfile_dict["y"] = y
        soundfile_dict["sr"] = sr
    except:
        pass
    return soundfile_dict
