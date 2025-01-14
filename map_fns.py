import numpy as np
import torch
from pyflink.common import Types
from pyflink.datastream import MapFunction
from pyflink.datastream.state import ListStateDescriptor
from pywhispercpp.model import Model
from silero_vad import VADIterator

from models import vad_model


class SpeechToTextMapFunction(MapFunction):
    def __init__(self):
        self.whisper_model = None
        self.buffer_state = None
        self.buffer_state_updated = False
        self.vad_iterator = None
        self.sampling_rate = 16000
        self.sample_size = 512

    def open(self, runtime_context):
        self.vad_iterator = VADIterator(vad_model, sampling_rate=self.sampling_rate,
                                        min_silence_duration_ms=1000)  # , speech_pad_ms=1000)
        self.whisper_model = Model('base.en')
        self.buffer_state = runtime_context.get_list_state(
            ListStateDescriptor("buffer", Types.LIST(Types.FLOAT()))
        )

    def map(self, value):
        arr = value[0]  # (512,)  # Tuple[numpy.ndarray]
        chunk = torch.from_numpy(arr)
        if len(chunk) < self.sample_size:
            # we can pad the last chunk, or we can signal that it's the end of the record and break the loop
            # chunk = f.pad(chunk, (0, 512 - chunk.size(dim=0)))
            return
        speech_dict = self.vad_iterator(chunk)
        if speech_dict:
            if 'start' in speech_dict:
                self.buffer_state.add(chunk.numpy().tolist())
                self.buffer_state_updated = True
            elif 'end' in speech_dict:
                buffer = self.buffer_state.get()
                numpy_arrays = [np.array(arr, dtype=np.float32) for arr in buffer]
                np_arr = np.concatenate(numpy_arrays)
                # noinspection PyUnusedLocal
                segments = self.whisper_model.transcribe(np_arr, new_segment_callback=print)
                self.buffer_state_updated = False
                self.buffer_state.clear()
        if self.buffer_state_updated:
            self.buffer_state.add(chunk.numpy().tolist())
        return ""
