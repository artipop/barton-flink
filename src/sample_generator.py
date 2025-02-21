import wave
from typing import Any, Union

import numpy as np
import soundfile as sf
from numpy import ndarray, dtype
from py4j.java_gateway import JavaObject
from pydub import AudioSegment
import time
from time import sleep

from pyflink.datastream import SourceFunction, FlatMapFunction


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


def audio_samples_generator(file_path, chunk_size=1024):
    """
    Генератор, который читает аудиофайл и возвращает блоки сэмплов
    со скоростью воспроизведения.

    :param file_path: Путь к аудиофайлу (WAV).
    :param chunk_size: Размер блока сэмплов.
    """
    with wave.open(file_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        block_duration = chunk_size / sample_rate
        data = wf.readframes(chunk_size)
        while data:
            yield data  # Возвращаем текущий блок
            time.sleep(block_duration)  # Ждем в соответствии с реальным временем
            data = wf.readframes(chunk_size)


def read_audio_in_chunks(file_path, chunk_size):
    with sf.SoundFile(file_path, mode='r') as audio_file:
        print('audio length in seconds: {}'.format(audio_file.frames / audio_file.samplerate))
        while True:
            data = audio_file.read(chunk_size, dtype='float32')
            # data, sr = audio_file.read(chunk_size, dtype='float32')
            # if np.ndim(data) > 1:
            #     data = np.mean(data, axis=0)
            # if len(data) == 0:
            if len(data) == 0:
                break
            yield data


# def read_audio_in_chunks(file_path, chunk_size):
#     with sf.SoundFile(file_path, 'r') as audio_file:
#         sample_rate = audio_file.samplerate
#         print(sample_rate)
#         chunk_duration = chunk_size / sample_rate  # Длительность блока в секундах
#         while True:
#             chunk = audio_file.read(chunk_size, dtype='float32')
#             if len(chunk) == 0:
#                 break
#             yield chunk
#             time.sleep(chunk_duration)


def read_samples_in_real_time(file_path):
    # Открываем аудиофайл
    with sf.SoundFile(file_path) as f:
        sample_rate = f.samplerate
        block_size = 1024  # Размер блока (количество сэмплов)

        # Читаем блоками и обрабатываем
        for block in f.blocks(blocksize=block_size):
            print(block)  # Здесь вы можете обработать сэмплы
            time.sleep(len(block) / sample_rate)  # Ждем реальное время


class DelayedSource(SourceFunction):
    def __init__(self, file_path, chunk_size, source_func: Union[str, JavaObject]):
        """
        :param data: список данных, которые будут отправляться в поток
        :param delay: задержка между отправкой элементов (в секундах)
        """
        super().__init__(source_func)
        self.file_path = file_path
        self.chunk_size = chunk_size

    def run(self, ctx):
        with sf.SoundFile(self.file_path, 'r') as audio_file:
            sample_rate = audio_file.samplerate
            print(sample_rate)
            chunk_duration = self.chunk_size / sample_rate  # Длительность блока в секундах
            while True:
                chunk = audio_file.read(self.chunk_size, dtype='float32')
                if len(chunk) == 0:
                    break
                # yield chunk
                ctx.collect(chunk)  # Отправляем элемент в поток
                time.sleep(chunk_duration)

    # def cancel(self):
        # self.is_running = False


class DelayedFlatMapFunction(FlatMapFunction):
    def __init__(self, chunk_size, sample_rate):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate

    def flat_map(self, value):
        chunk_duration = self.chunk_size / self.sample_rate
        time.sleep(chunk_duration)
        print(chunk_duration)
        return value
