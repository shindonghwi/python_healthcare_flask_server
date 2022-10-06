import librosa
import librosa.display


def load_librosa(audio_path, sample_rate=16000) -> dict:
    librosa_dict = {"y": None, "sr": None}
    try:
        y, sr = librosa.load(audio_path, sr=sample_rate)
        librosa_dict["y"] = y
        librosa_dict["sr"] = sr
    except:
        pass
    return librosa_dict
