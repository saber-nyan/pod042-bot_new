FROM python:3.8-slim-buster

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update \
	&& apt install -y --no-install-recommends eatmydata \
	&& eatmydata apt install -y --no-install-recommends ffmpeg libavcodec-extra curl \
	&& eatmydata apt clean

WORKDIR /app/
COPY . ./

RUN pip install --no-cache .

CMD ["python", "-m", "pod042_bot"]
