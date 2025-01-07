from typing import Iterable, Tuple

import numpy as np
from pyflink.datastream import ProcessWindowFunction, WindowFunction
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

## using VADIterator class

vad_iterator = VADIterator(model, sampling_rate=SAMPLING_RATE)
wav = read_audio(f'/Users/artem/dev/outsource/flink/barton-flink/vidal.mp3', sampling_rate=SAMPLING_RATE)

model = Model('base.en')

# only 2 frame sizes are supported by silero: 256 and 512
window_size_samples = 512 if SAMPLING_RATE == 16000 else 256
for i in range(0, len(wav), window_size_samples):
    chunk: Tensor = wav[i: i + window_size_samples]
    if len(chunk) < window_size_samples:
        break
    speech_dict = vad_iterator(chunk, return_seconds=True)  # when someone speaks
    if speech_dict:
        # speech_dict['start']
        # speech_dict['end']
        print(speech_dict, end='\n')
        np_arr = chunk.detach().cpu().numpy()  # np.ndarray
        np_arr = np.concatenate([np_arr, np.zeros((int(SAMPLING_RATE) + 10))])
        segments = model.transcribe(np_arr, new_segment_callback=print)  #, new_segment_callback=self._new_segment_callback)
        print(len(segments))
vad_iterator.reset_states()  # reset model states after each audio ... TODO: we can reset it after each speech found

## just probabilities

# speech_probs = []
# window_size_samples = 512 if SAMPLING_RATE == 16000 else 256
# for i in range(0, len(wav), window_size_samples):
#     chunk = wav[i: i + window_size_samples]
#     if len(chunk) < window_size_samples:
#         break
#     speech_prob = model(chunk, SAMPLING_RATE).item()
#     speech_probs.append(speech_prob)
# model.reset_states()  # reset model states after each audio
#
# print(speech_probs[:10])  # first 10 chunks predicts
