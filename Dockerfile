FROM ubuntu
RUN apt update && apt install -y wget python3 unzip jq mkvtoolnix timewarrior python3-pip

RUN pip3 install --upgrade google-api-python-client oauth2client progressbar2 python-dateutil

RUN wget https://github.com/tokland/youtube-upload/archive/master.zip && \
  unzip master.zip

ADD https://raw.githubusercontent.com/Anvil/bash-argsparse/master/argsparse.sh /
RUN chmod a+x argsparse.sh

ADD upload-recordings.py /
ADD process-videos.cmd /

ENTRYPOINT [ "bash", "process-videos.cmd" ]
