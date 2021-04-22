FROM python:3.8.3

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update -y && \
    apt-get install --auto-remove -y \
      binutils \
      libproj-dev \
      gdal-bin \
      postgis \
      curl \
      locales \
      netcat \
      apt-transport-https && \
    rm -rf /var/lib/apt/lists/*


RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && /usr/sbin/locale-gen


RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt



COPY . .


