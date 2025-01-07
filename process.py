import argparse
import sys

from pyflink.common import Encoder, Duration, Types, Time
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig, \
    RollingPolicy
from pyflink.datastream.window import SlidingEventTimeWindows

from test_util import generate_audio_stream_mp3
from vad.vad_process_windows import SileroVadProcessWindowFunction


def vad_processing(input_path: str, output_path: str):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    # write all the data to one file
    env.set_parallelism(1)

    # for chunk in generate_audio_stream_mp3(input_path):
    #     print(chunk)

    # define the source
    ds = env.from_collection(
        [(chunk,) for chunk in generate_audio_stream_mp3(input_path)],
        type_info=Types.TUPLE([Types.LIST(Types.INT())])
    )

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

    ds \
        .key_by(lambda x: 0) \
        .window(SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(5))) \
        .reduce(function) \
        .map(lambda x: print(x))

    (ds
     .key_by(lambda x: 0)
     .window(SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(5)))
     # or
     # .window(TumblingProcessingTimeWindows.of(Time.milliseconds(window_size_ms)))
     .process(SileroVadProcessWindowFunction()))

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

    # submit for execution
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

    an_input = '/Users/artem/dev/outsource/flink/barton-flink/vidal.mp3'  # known_args.input
    vad_processing(an_input, known_args.output)
