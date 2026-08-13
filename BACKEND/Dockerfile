FROM python:3.11-slim

WORKDIR /app

# Install dependencies needed for some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Start script to run migrations and then start the server
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
