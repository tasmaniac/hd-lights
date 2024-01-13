FROM ubuntu:22.04
LABEL maintainer="contact@devopscube.com" 
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.5 \
    python3-pip \
    hdparm
COPY files/main.py /tmp/main.py
RUN pip3 install requests blkinfo
RUN mkdir /data
# CMD ["python3 /tmp/main.py"]
