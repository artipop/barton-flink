import wave
from typing import Any

import numpy as np
import soundfile as sf
from numpy import ndarray, dtype
from pydub import AudioSegment


def generate_audio_stream_mp3(file_path, chunk_duration_ms=100):
    audio = AudioSegment.from_file(file_path, format="mp3")

    num_chunks = len(audio) // chunk_duration_ms

    for i in range(num_chunks):
        chunk = audio[i * chunk_duration_ms: (i + 1) * chunk_duration_ms]

        samples: ndarray[Any, dtype[Any]] = np.array(chunk.get_array_of_samples())

        yield samples
        # if audio.channels == 2:
        #     samples = samples.reshape((-1, 2))
        # yield samples.tolist()
        # if audio.channels == 2:
        #     # list of primitives/scalars
        #     samples = samples.reshape(-1).tolist()
        # else:
        #     # list of primitives/scalars
        #     samples = samples.tolist()
        yield samples


def generate_audio_stream(file_path: str, chunk_size: int = 1024):
    with wave.open(file_path, 'rb') as wf:
        sample_width = wf.getsampwidth()
        while True:
            data = wf.readframes(chunk_size)
            if not data:
                break
            samples: list[int] = [int.from_bytes(data[i:i + sample_width], byteorder='little', signed=True)
                                  for i in range(0, len(data), sample_width)]
            yield samples


def read_audio_in_chunks(file_path, chunk_size):
    with sf.SoundFile(file_path, 'r') as audio_file:
        while True:
            data = audio_file.read(chunk_size, dtype='float32')
            if len(data) == 0:
                break
            yield data
