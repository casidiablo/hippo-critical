FROM ubuntu
RUN apt update && apt install -y wget python3 unzip jq mkvtoolnix timewarrior python3-pip

RUN pip3 install --upgrade google-api-python-client oauth2client progressbar2 python-dateutil

RUN mkdir /app

RUN wget https://github.com/tokland/youtube-upload/archive/master.zip -O youtube-upload.zip && \
    unzip youtube-upload.zip && \
    mv /youtube-upload-master /app/youtube-upload && \
    rm youtube-upload.zip

ADD https://raw.githubusercontent.com/Anvil/bash-argsparse/master/argsparse.sh /app
RUN chmod a+x /app/argsparse.sh

ADD align-users.sh /app/
RUN chmod a+x /app/align-users.sh

ADD upload-recordings.py /app/
ADD process-videos.mcd /app/process-videos

# allow any user to read the code of this app
RUN chmod a+r -R /app

ENTRYPOINT [ "bash", "/app/process-videos" ]
