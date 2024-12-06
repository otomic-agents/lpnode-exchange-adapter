# Build stage
FROM python:3.12 AS build

# Add application code to the image
ADD ./ /data/app/

# Set working directory
WORKDIR /data/app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g ts-node nodemon && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js project dependencies
WORKDIR /data/app/otmoic-ccxt-market
RUN npm install

# Slim stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from the build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy application code and Node.js dependencies from the build stage
COPY --from=build /data/app .

# Install Node.js and global tools
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g ts-node nodemon && \
    apt-get clean && rm -rf /var/lib/apt/lists/*