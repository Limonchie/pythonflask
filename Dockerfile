FROM surnet/alpine-wkhtmltopdf:3.18.0-0.12.6-full

ENV PYTHONUNBUFFERED=1
ENV DOCS_PATH=/docs
ENV CONTRACTS_PATH=/contracts
ENV DOCS_TTL=3600

HEALTHCHECK --interval=5s --timeout=10s --retries=3 CMD curl -sS http://127.0.0.1:80/status || exit 1

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python && python3 -m ensurepip \
&& pip3 install --no-cache --upgrade pip setuptools && mkdir /docs && mkdir /contracts

ENTRYPOINT []
WORKDIR /app
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt && apk --no-cache add curl

CMD gunicorn -b 0.0.0.0:80 -w 2 --timeout 120 --log-level=info chinaekb-forms:app

