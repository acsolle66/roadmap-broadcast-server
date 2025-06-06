# Async Broadcast Server and Client

A simple asynchronous TCP broadcast system built with Python's `asyncio`. The server supports multiple clients, handles messaging and basic commands, and includes timeout handling. The client supports input, server messages, and a heartbeat mechanism. This project is based on a roadmap task to build a **CLI tool** that starts a **broadcast server**.   
https://roadmap.sh/projects/broadcast-server

## 🚀 Features
### Server
- Asynchronous handling of multiple client connections
- Basic verification handshake using a `CONNECT` message
- Broadcasts messages from any client to all others
- Built-in command support:
  - `\\exit`: disconnects the client
  - `\\clients`: lists all connected clients
  - `\\ping`: silent heartbeat
- Automatic client timeout disconnection
- Graceful shutdown of connections
- Logging via a custom logger module

### Client
- Verifies connection with the server
- Async input from stdin
- Receives messages from server
- Sends periodic heartbeats to maintain the connection
- Cancels tasks on exit or error
   

## ⚙️ Usage
### 📦 Requirements
- Python 3.11+
- No external dependencies (pure standard library)

### Running the Server

```bash
python main_server.py
```
This starts the server on the specified host and port.

#### 🔧 CLI Arguments
| Argument | Description |
| -------- | ----------- |
| --host | Broadcast server host (default: '127.0.0.1') |
| --port | Broadcast server port (default: 8888) |

### Running the Client
```bash
python main_client.py 
```  
On startup, the client connects to the server, sends a verification message (CONNECT <username>), and starts listening for input and incoming messages.

#### 🔧 CLI Arguments
| Argument | Description |
| -------- | ----------- |
| --host | Broadcast server host (default: '127.0.0.1') |
| --port | Broadcast server port (default: 8888) |
| --user | Username (default: anonymous) |

## Docker
### Build the Docker images
```bash
# Run the commands from the project root
docker build -f docker/server/Dockerfile -t broadcast-server .
docker build -f docker/client/Dockerfile -t broadcast-client .
```
### Run the containers
```bash
# Create an isolated Docker network so clients can reach the server by name
docker network create broadcast-net

#Run the server   
docker run --network broadcast-net --rm -it --name broadcastserver broadcast-server

# Run the client(s) in a separate terminal  
# Note: --host broadcastserver tells the client to connect to the server container 
docker run --network broadcast-net --rm -it broadcast-client --host broadcastserver
```
⚠️ Make sure to include -it when running the client so interactive input (stdin) works inside the container.

## ⚠️ Known Limitations
- Linux-only: The client relies on `sys.stdin.readline()` with run_in_executor, which behaves correctly only on Unix-like systems (Linux). Windows users may experience blocking or undefined behavior.

- Blocking Input: The client uses `run_in_executor()` for terminal input. This operation is not cancellable and will wait indefinitely until input is received. When exiting the client (e.g., after typing \\exit), you must press Enter to allow the program to cleanly shut down.

## Example

Start the server:
```bash
python main_server.py --port 6969
```

In another terminal, run the client:
```bash
python client.py --port 6969 --user Attila
```
Commands:
- Send a message to all users by typing and pressing Enter.
- Use `\\exit` to leave the client.
- Use `\\clients` to see active clients.