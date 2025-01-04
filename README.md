# Barton Flink

## How to run
- Install Java
- Install python
- Create venv and install required packages
  - `pip3 install apache-flink`
- Then run `python3 main.py` or submit the job on the cluster ([instruction](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/cli/#submitting-pyflink-jobs))

### Notes
- Only one python binding [pywhispercpp](https://github.com/absadiki/pywhispercpp) supports GPU
  - and this binding can be built like [this](https://github.com/ggerganov/whisper.cpp/issues/9#issuecomment-2162975700)
