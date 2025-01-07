import wave

from pydub import AudioSegment
import numpy as np


def generate_audio_stream_mp3(file_path, chunk_duration_ms=100):
    audio = AudioSegment.from_file(file_path, format="mp3")

    num_chunks = len(audio) // chunk_duration_ms

    for i in range(num_chunks):
        chunk = audio[i * chunk_duration_ms: (i + 1) * chunk_duration_ms]

        samples = np.array(chunk.get_array_of_samples())
        # if audio.channels == 2:
        #     samples = samples.reshape((-1, 2))
        # yield samples.tolist()
        if audio.channels == 2:
            samples = samples.reshape(-1).tolist()
        else:
            samples = samples.tolist()
        yield samples


def generate_audio_stream(file_path: str, chunk_size: int = 1024):
    with wave.open(file_path, 'rb') as wf:
        sample_width = wf.getsampwidth()
        while True:
            data = wf.readframes(chunk_size)
            if not data:
                break
            yield [
                int.from_bytes(data[i:i + sample_width], byteorder='little', signed=True)
                for i in range(0, len(data), sample_width)
            ]
