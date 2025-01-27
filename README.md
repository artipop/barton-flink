# Captain Flink

## How to run
- Install Java (version 11 is the [recommended one](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/deployment/java_compatibility/))
- Install Python (3.11)
- Create venv and install required packages
  - `pip install apache-flink`
  - `pip install silero-vad` and `pip install soundfile` (needed for audio I/O, see other [options](https://github.com/snakers4/silero-vad/wiki/Examples-and-Dependencies#dependencies))
  - depending on the system
    - for macOS: `WHISPER_COREML=1 pip install git+https://github.com/absadiki/pywhispercpp`
    - for Nvidia GPU: `GGML_CUDA=1 pip install git+https://github.com/absadiki/pywhispercpp`
  - also for mp3 testing `pip install pydub` + ffmpeg should be installed (installation method depends on the OS)
- Then run `python3 main.py` or submit the job on the cluster ([instruction](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/cli/#submitting-pyflink-jobs))

To submit a job on a cluster read [this](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/deployment/cli/).

### Notes
#### Whisper
- Only one python binding [pywhispercpp](https://github.com/absadiki/pywhispercpp) supports GPU
  - and this binding can be built like [this](https://github.com/ggerganov/whisper.cpp/issues/9#issuecomment-2162975700)
- For CoreML this [model](https://huggingface.co/ggerganov/whisper.cpp/blob/main/ggml-base.en-encoder.mlmodelc.zip) should be downloaded and moved to `/${USER_HOME}/Library/Application Support/pywhispercpp/models`

#### VAD
- pyannote audio
- Silero VAD
- webrtcvad
