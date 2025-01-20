from pywhispercpp.model import Model
from silero_vad import load_silero_vad

whisper_model = Model('base.en')
vad_model = load_silero_vad()
