FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1 \
    USOS_CFG_DIR=/data/cfgs \
    USOS_DB_PATH=/data/plan.db3

WORKDIR /app

RUN apk add --no-cache dcron

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/cfgs && touch /data/plan.db3

COPY docker/update-cron /etc/crontabs/root
RUN chmod 0600 /etc/crontabs/root

EXPOSE 8000

CMD ["sh", "-c", "crond -b -l 2 && uvicorn cli.serve:app --host 0.0.0.0 --port 8000"]