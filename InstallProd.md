```shell
sudo apt update
sudo apt install openjdk-11-jdk
```

```shell
wget https://dlcdn.apache.org/flink/flink-1.20.0/flink-1.20.0-bin-scala_2.12.tgz
tar -xzf flink-*.tgz
```

sudo apt install git

```shell
curl -fsSL https://pyenv.run | bash
# build deps
sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

bashrc and profile - https://github.com/pyenv/pyenv?tab=readme-ov-file#bash

install python 3.11
```shell
pyenv install 3.11
pyenv global 3.11
```

sudo apt update
sudo apt install ffmpeg

git clone https://github.com/artipop/barton-flink.git
cd barton-flink
python3 -m venv .venv
source .venv/bin/activate

cd flink-1.20.0
./bin/start-cluster.sh
