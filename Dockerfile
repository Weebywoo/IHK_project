FROM ubuntu:latest
FROM python:3.13.3-slim

RUN apt-get -y update
RUN apt-get -y install git

WORKDIR /usr/src/IHK_project
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 0
EXPOSE 8000

ENTRYPOINT ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--log-level", "debug"]