
FROM python:3.8.2-alpine

# Installing gcc and other necessary dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Upgrading pip and install required Python packages
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir Flask flask_prometheus_metrics Flask-SQLAlchemy

# Exposing port 5000
EXPOSE 5000

# Creatin an /app directory
RUN mkdir /app

# Copy the necessary files and directories to /app
COPY app.py /app
COPY templates /app/templates

# running the Flask application
CMD ["python", "/app/app.py"]
