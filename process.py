import argparse
import sys
from typing import Any

import numpy as np
import torch
from pyflink.common import Types
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode, MapFunction
from pyflink.datastream.state import ListStateDescriptor
from pywhispercpp.model import Model
from silero_vad import VADIterator, load_silero_vad

from test_util import generate_audio_stream_mp3, read_audio_in_chunks

SAMPLING_RATE = 16000


class SentimentAnalysis(MapFunction):
    def __init__(self):
        self.wh_model = None
        self.buffer_state = None
        self.buffer_state_updated = False
        self.vad_iterator = None

    def open(self, runtime_context):
        model = load_silero_vad()
        self.vad_iterator = VADIterator(model, sampling_rate=SAMPLING_RATE,
                                        min_silence_duration_ms=1000)  # , speech_pad_ms=1000)
        self.wh_model = Model('base.en')
        self.buffer_state = runtime_context.get_list_state(
            ListStateDescriptor("buffer", Types.LIST(Types.FLOAT()))
        )

    def map(self, value):
        # def process_element(self, value: Tuple[numpy.ndarray], ctx):
        # Example of simple sentiment analysis logic
        arr = value[0]
        # print(type(arr))  # <class 'numpy.ndarray'>
        chunk = torch.from_numpy(arr)
        # print(type(chunk))  # <class 'torch.Tensor'>
        if len(chunk) < 512:
            # мы можем последний чанк дозаполнять нулями либо просто выйти из цикла
            # chunk = f.pad(chunk, (0, 512 - chunk.size(dim=0)))
            return
        speech_dict = self.vad_iterator(chunk)
        if speech_dict:
            # TODO: COLLECT BUFFER
            print(speech_dict)
            if 'start' in speech_dict:
                self.buffer_state.add(chunk.numpy().tolist())
                self.buffer_state_updated = True
            elif 'end' in speech_dict:
                buffer = self.buffer_state.get()
                numpy_arrays = [np.array(arr, dtype=np.float32) for arr in buffer]
                np_arr = np.concatenate(numpy_arrays)
                segments = self.wh_model.transcribe(np_arr, new_segment_callback=print)
                self.buffer_state_updated = False
                self.buffer_state.clear()
        if self.buffer_state_updated:
            self.buffer_state.add(chunk.numpy().tolist())
        return ""


whisper_model = Model('base.en')


def transcribe(arr: np.ndarray):
    segments = whisper_model.transcribe(arr, new_segment_callback=print)


def vad_processing(input_path: str, output_path: str):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    # write all the data to one file
    env.set_parallelism(1)

    # for chunk in generate_audio_stream_mp3(input_path):
    #     print(chunk)

    # define the source
    if input_path.endswith(".mp3"):
        generator = generate_audio_stream_mp3(input_path)
    elif input_path.endswith(".wav"):
        generator = read_audio_in_chunks(input_path, 512)
    else:
        raise Exception("Unsupported file type")
    ds = env.from_collection(
        [(chunk,) for chunk in generator],
        # type_info=Types.TUPLE([Types.PRIMITIVE_ARRAY(Types.INT())])
    )
    # ds.print()
    # assigner = (WatermarkStrategy.for_monotonous_timestamps()
    #             .with_timestamp_assigner(timestamp_assigner=MyTsAss()))
    # ds.assign_timestamps_and_watermarks(assigner)

    (ds
     .key_by(lambda x: 0)
     .map(SentimentAnalysis()))

    # (ds
    #  .key_by(lambda x: 0)
    #  .process(SentimentAnalysis()))

    # return None

    # ds = env.from_source(
    #     source=FileSource.for_record_stream_format(StreamFormat.text_line_format(),
    #                                                input_path)
    #     .process_static_file_set().build(),
    #     watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
    #     source_name="file_source"
    # )
    # ds.set_buffer_timeout()
    def function(x, y):
        print('function')
        print(x)
        print(y)
        return {
            x + y
        }

    env.execute()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to process.')
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='Output file to write results to.')

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    an_input = '/Users/artem/dev/outsource/flink/barton-flink/vidal.wav'  # known_args.input
    vad_processing(an_input, known_args.output)
