FROM python:3.8

WORKDIR /home

ENV TELEGRAM_API_TOKEN="1798389140:AAFAIr3PJv4sTLrkFGgjEs9h06yNnquZD_s"
ENV TELEGRAM_ACCESS_ID=""
ENV TELEGRAM_PROXY_URL=""
ENV TELEGRAM_PROXY_LOGIN=""
ENV TELEGRAM_PROXY_PASSWORD=""

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram pytz && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]

