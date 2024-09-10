FROM python:3.10-slim

# Create a directory for the application
WORKDIR /app

# Copy the application code and requirements file
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set the environment variables from .env file
ENV TELEGRAM_API_TOKEN=""
ENV TELEGRAM_CHAT_ID=""
ENV ALCHEMY_RPC_URL=""

# Expose the port for Prometheus (if using)
EXPOSE 9091

# Command to run the application
CMD ["python", "app.py"]
