import wave


def generate_audio_stream(file_path: str, chunk_size: int = 1024):
    with wave.open(file_path, 'rb') as wf:
        sample_width = wf.getsampwidth()
        while True:
            data = wf.readframes(chunk_size)
            if not data:
                break
            yield [
                int.from_bytes(data[i:i + sample_width], byteorder='little', signed=True)
                for i in range(0, len(data), sample_width)
            ]
