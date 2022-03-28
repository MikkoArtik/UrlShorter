FROM debian:bullseye-slim

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y curl
RUN apt-get install -y python3 python3-distutils

RUN apt-get -y install wget && wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

ENV APP_FOLDER=/url-shorter

RUN mkdir $APP_FOLDER

COPY ./requirements.txt $APP_FOLDER
RUN pip install -r $APP_FOLDER/requirements.txt

COPY . $APP_FOLDER
WORKDIR $APP_FOLDER

ENTRYPOINT ["supervisord", "-c", "/url-shorter/supervisord.conf"]