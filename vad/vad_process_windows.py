from typing import Iterable, Tuple

from pyflink.datastream import ProcessWindowFunction
from silero_vad import read_audio, VADIterator, load_silero_vad


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


model = load_silero_vad()

SAMPLING_RATE = 16000

## using VADIterator class

vad_iterator = VADIterator(model, sampling_rate=SAMPLING_RATE)
wav = read_audio(f'en_example.wav', sampling_rate=SAMPLING_RATE)

window_size_samples = 512 if SAMPLING_RATE == 16000 else 256
for i in range(0, len(wav), window_size_samples):
    chunk = wav[i: i+ window_size_samples]
    if len(chunk) < window_size_samples:
      break
    speech_dict = vad_iterator(chunk, return_seconds=True)
    if speech_dict:
        print(speech_dict, end=' ')
vad_iterator.reset_states() # reset model states after each audio

## just probabilities

wav = read_audio('en_example.wav', sampling_rate=SAMPLING_RATE)
speech_probs = []
window_size_samples = 512 if SAMPLING_RATE == 16000 else 256
for i in range(0, len(wav), window_size_samples):
    chunk = wav[i: i+window_size_samples]
    if len(chunk) < window_size_samples:
        break
    speech_prob = model(chunk, SAMPLING_RATE).item()
    speech_probs.append(speech_prob)
model.reset_states() # reset model states after each audio

print(speech_probs[:10]) # first 10 chunks predicts
