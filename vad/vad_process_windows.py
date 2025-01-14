from typing import Iterable, Tuple

import numpy as np
import torch.nn.functional as f
from pyflink.datastream import ProcessWindowFunction
from pywhispercpp.model import Model
from silero_vad import read_audio, VADIterator, load_silero_vad
from torch import Tensor


class SileroVadProcessWindowFunction(ProcessWindowFunction):
    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Tuple[str, int]]) -> Iterable[str]:
        count = 0
        for _ in elements:
            count += 1
        yield "Window: {} count: {}".format(context.window(), count)


class PyannoteVadProcessWindowFunction(ProcessWindowFunction):
    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Tuple[str, int]]) -> Iterable[str]:
        count = 0
        for _ in elements:
            count += 1
        yield "Window: {} count: {}".format(context.window(), count)


# class SilenceWindowFunction(WindowFunction):
#     def apply(self, key, window, inputs, collector):
#         pass


model = load_silero_vad()

SAMPLING_RATE = 16000
# SAMPLING_RATE = 8000

## using VADIterator class

vad_iterator = VADIterator(model, sampling_rate=SAMPLING_RATE, min_silence_duration_ms=1000)  #, speech_pad_ms=1000)
# wav: Tensor = read_audio('/Users/artem/dev/outsource/flink/barton-flink/vidal.wav', sampling_rate=SAMPLING_RATE)
wav: Tensor = read_audio('/Users/artem/dev/outsource/flink/barton-flink/audio.wav', sampling_rate=SAMPLING_RATE)

whisper_model = Model('base.en')
# segments = whisper_model.transcribe('../vidal.wav', new_segment_callback=print)
# for segment in segments:
#     print(segment.text)

# np_arr = np.zeros(512, dtype=np.float32)
# np_arr = np.ndarray(tuple(range(512)))

start = 0
end = 0

speech_chunks = []

# only 2 frame sizes are supported by silero: 256 and 512
window_size_samples = 512 if SAMPLING_RATE == 16000 else 256


def is_started():
    return len(speech_chunks) > 0


def transcribe(arr: np.ndarray):
    segments = whisper_model.transcribe(arr, new_segment_callback=print)


for i in range(0, len(wav), window_size_samples):
    chunk: Tensor = wav[i: i + window_size_samples]
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
