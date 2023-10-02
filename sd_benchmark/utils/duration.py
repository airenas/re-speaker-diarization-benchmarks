import wave


def duration(file):
    with wave.open(file, 'rb') as wav_file:
        num_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()
        return num_frames / frame_rate
