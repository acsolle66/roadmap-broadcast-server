# Official Python 3.11 image from Docker hub
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /broadcast-server

# Copy the app into the container
COPY broadcast_server/ ./broadcast_server/
COPY utils/ ./utils/
COPY main_server.py .

# Program entrypoint
ENTRYPOINT [ "python", "main_server.py" ]
CMD [ "--host", "0.0.0.0", "--port","8888" ]
