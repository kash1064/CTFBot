FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt update
COPY .env .
COPY src/requirements.txt src/
RUN cd src && pip3 install -r requirements.txt

COPY src/bot.py src/
USER nobody
CMD ["python", "src/bot.py"]