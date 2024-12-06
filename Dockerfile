FROM python:3.12 AS build
ADD ./ /data/app/
WORKDIR /data/app/

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g ts-node && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim

WORKDIR /app

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY --from=build /data/app .

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g ts-node nodemon && \
    apt-get clean && rm -rf /var/lib/apt/lists/*