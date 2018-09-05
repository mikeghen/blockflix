FROM python:3.6
MAINTAINER Michael Ghen<datascience@bdtrust.org>
RUN apt-get dist-upgrade
RUN apt-get update
RUN apt-get -y install cron
RUN curl -sL https://deb.nodesource.com/setup_8.x |  bash -
RUN apt-get install -y nodejs
RUN npm install -g n
RUN n stable

WORKDIR /opt/blockflix
ADD requirements /opt/blockflix/requirements
ADD package.json /opt/blockflix/package.json
RUN pip install -r requirements/dev.txt
RUN npm install

ADD . /opt/blockflix

RUN node --version

EXPOSE 5000
EXPOSE 2992

ENV FLASK_APP autoapp.py
RUN npm run build

ENTRYPOINT ["./script/entrypoint.sh"]
