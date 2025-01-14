import argparse
import logging
import sys

from pyflink.common import Encoder, Time
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig, \
    RollingPolicy
from pyflink.datastream.window import SlidingEventTimeWindows

from map_fns import SpeechToTextMapFunction
from sample_generator import generate_audio_stream_mp3, read_audio_in_chunks


def audio_processing(input_path: str, output_path: str):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    env.set_parallelism(1)

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
    (ds
     .key_by(lambda x: 0)
     .map(SpeechToTextMapFunction()))

    # ds.set_buffer_timeout()  # ???

    # assigner = (WatermarkStrategy.for_monotonous_timestamps()
    #             .with_timestamp_assigner(timestamp_assigner=SimpleTimestampAssigner()))
    # ds.assign_timestamps_and_watermarks(assigner)

    env.execute()

    (ds
     .key_by(lambda x: 0)
     .window(SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(5)))
     # or
     # .window(TumblingProcessingTimeWindows.of(Time.milliseconds(window_size_ms)))
     # .process(SileroVadProcessWindowFunction())
     # or
     # .map(SileroVadMapFunction())
     )

    # send processing result to output file or stdout
    if output_path is not None:
        ds.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path,
                encoder=Encoder.simple_string_encoder())
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("prefix")
                .with_part_suffix(".ext")
                .build())
            .with_rolling_policy(RollingPolicy.default_rolling_policy())
            .build()
        )
    else:
        print("Printing result to stdout. Use --output to specify output path.")
        ds.print()

    env.execute()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

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

    audio_processing(known_args.input, known_args.output)
