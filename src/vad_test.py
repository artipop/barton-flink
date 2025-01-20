import numpy as np
import torch.nn.functional as f
from models import vad_model, whisper_model
from silero_vad import read_audio, VADIterator

SAMPLING_RATE = 16000
# SAMPLING_RATE = 8000

vad_iterator = VADIterator(vad_model, sampling_rate=SAMPLING_RATE,
                           min_silence_duration_ms=1000)  # , speech_pad_ms=1000)
wav = read_audio('/audio.wav', sampling_rate=SAMPLING_RATE)

speech_chunks = []

# only 2 frame sizes are supported by silero-vad: 256 and 512
window_size_samples = 512 if SAMPLING_RATE == 16000 else 256


def is_started():
    return len(speech_chunks) > 0


def transcribe(arr: np.ndarray):
    # noinspection PyUnusedLocal
    segments = whisper_model.transcribe(arr, new_segment_callback=print)


for i in range(0, len(wav), window_size_samples):
    chunk = wav[i: i + window_size_samples]
    if len(chunk) < window_size_samples:
        # we can pad the last chunk, or we can signal that it's the end of the record and break the loop
        chunk = f.pad(chunk, (0, 512 - chunk.size(dim=0)))
        break
    speech_dict = vad_iterator(chunk)
    if speech_dict:
        if 'start' in speech_dict:
            chunk_numpy = chunk.numpy()
            speech_chunks.append(chunk_numpy)
        elif 'end' in speech_dict:
            np_arr = np.concatenate(speech_chunks)
            transcribe(np_arr)
            speech_chunks = []
    if is_started():
        speech_chunks.append(chunk.numpy())
vad_iterator.reset_states()
