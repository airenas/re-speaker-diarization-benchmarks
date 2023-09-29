FROM openjdk:22-slim-bullseye

WORKDIR /app

RUN apt update && apt install -y \
    wget

RUN wget --no-check-certificate https://git-lium.univ-lemans.fr/Meignier/lium-spkdiarization/-/raw/master/jar/LIUM_SpkDiarization-4.2.jar

RUN mkdir -p /app/jar && cd /app/jar && jar -xvf /app/LIUM_SpkDiarization-4.2.jar
ENV LOCALCLASSPATH=/app/LIUM_SpkDiarization-4.2.jar
ENV JAVA_BIN=java

COPY run.sh /app/

