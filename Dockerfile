FROM ubuntu:14.04

RUN useradd -m -d /home/judge -p judge judge && chsh -s /bin/bash judge

RUN apt-get update
RUN apt-get install -y time
RUN apt-get install -y build-essential
