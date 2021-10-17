FROM python:3.8.11

RUN apt-get update -y && apt-get upgrade -y &&\
  apt-get install vim git -y &&\
  apt-get autoremove -y &&\
  apt-get clean &&\
  rm -rf /usr/local/src/*

COPY requirements.txt requirements.txt
RUN pip install -U pip &&\
  pip install torch==1.7.1+cpu -f https://download.pytorch.org/whl/torch_stable.html &&\
  pip install --no-cache-dir -r requirements.txt 