FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /src
WORKDIR /src

COPY dailywheaterdigest/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt


RUN useradd -m admin
RUN chown -R admin /src
USER admin

EXPOSE 8000

COPY dailywheaterdigest ./