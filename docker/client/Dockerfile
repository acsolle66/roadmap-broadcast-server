# Official Python 3.11 image from Docker hub
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /broadcast-client

# Copy the app into the container
COPY broadcast_client/ ./broadcast_client/
COPY utils/ ./utils/
COPY main_client.py .

# Program entrypoint
ENTRYPOINT [ "python", "main_client.py" ]
CMD [ "--host", "127.0.0.1", "--port","8888" ,"--user", "anonymous"]
