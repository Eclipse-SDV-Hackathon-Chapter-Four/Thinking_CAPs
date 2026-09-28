# MQTT Broker Setup Instructions

This guide shows how to set up and run an Eclipse Mosquitto MQTT broker using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Project Structure

```
mqtt-broker/
├── docker-compose.yml
└── mosquitto.conf
```

## Quick Start

### 1. Create Project Directory

```bash
mkdir mqtt-broker
cd mqtt-broker
```

### 2. Add Configuration Files

Place the provided files in your project directory:
- `mosquitto.conf` → MQTT broker configuration
- `docker-compose.yml` → Docker service definition

### 3. Start the MQTT Broker

```bash
# Start the broker
docker-compose up

# Or run in background
docker-compose up -d
```

### 4. Verify the Broker is Running

```bash
# Check container status
docker-compose ps

# View broker logs
docker-compose logs mosquitto
```

## Broker Configuration

The MQTT broker is configured with:
- **Port**: 1883 (MQTT protocol)
- **WebSocket Port**: 9001 (for web clients)
- **Anonymous Access**: Enabled (no authentication required)
- **Message Persistence**: Enabled
- **Network**: Host mode (accessible on localhost:1883)

## Testing the Broker

### Using mosquitto_pub/mosquitto_sub (if installed locally)

```bash
# Subscribe to a topic (in one terminal)
mosquitto_sub -h localhost -p 1883 -t test/topic

# Publish a message (in another terminal)
mosquitto_pub -h localhost -p 1883 -t test/topic -m "Hello MQTT!"
```

### Using Docker containers

```bash
# Subscribe to a topic
docker run -it --rm --network host eclipse-mosquitto:2.0 mosquitto_sub -h localhost -t test/topic

# Publish a message
docker run -it --rm --network host eclipse-mosquitto:2.0 mosquitto_pub -h localhost -t test/topic -m "Hello MQTT!"
```

## Management Commands

### Start/Stop Services

```bash
# Start broker
docker-compose up -d

# Stop broker
docker-compose down

# Restart broker
docker-compose restart
```

### View Logs

```bash
# Follow logs in real-time
docker-compose logs -f mosquitto

# View recent logs
docker-compose logs --tail 50 mosquitto
```

### Access Broker Shell

```bash
# Access the container
docker-compose exec mosquitto sh
```

## Connection Details

- **MQTT Host**: `localhost` (or your server IP)
- **MQTT Port**: `1883`
- **WebSocket Port**: `9001`
- **Authentication**: None (anonymous allowed)
- **SSL/TLS**: Not configured (plain text)

## Troubleshooting

### Docker issues

#### Option 1: Add user to docker group (Recommended)

```bash
# Add your user to the docker group:
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Verify it works:
docker --version
```

#### Option 2: Use sudo (Quick fix)

```bash
# Run docker commands with sudo:
sudo docker run ...
sudo docker-compose up
```

#### Option 3: Fix docker socket permissions (Temporary)

```bash
# Change socket permissions (resets on reboot):
sudo chmod 666 /var/run/docker.sock
```

#### Option 4: Start Docker service

```bash
# Make sure Docker daemon is running
sudo systemctl start docker
sudo systemctl enable docker  # Enable auto-start on boot
```

#### Verify the fix:

```bash
# Test Docker without sudo:
docker ps
docker run hello-world
```


### Common Issues

1. **Port 1883 already in use**:
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep 1883
   
   # Stop conflicting service or change port in docker-compose.yml
   ```

2. **Permission denied errors**:
   ```bash
   # Ensure Docker has proper permissions
   sudo docker-compose up
   ```

3. **Container won't start**:
   ```bash
   # Check logs for errors
   docker-compose logs mosquitto
   ```

### Verify Broker Status

```bash
# Check if broker is accepting connections
telnet localhost 1883

# Or use netcat
nc -zv localhost 1883
```

## Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

## Next Steps

Once your broker is running, you can:
- Connect MQTT clients to `localhost:1883`
- Use web-based MQTT clients via WebSocket on port `9001`
- Integrate with IoT devices and applications
- Monitor message traffic through the logs

The broker is now ready to handle MQTT publish/subscribe operations!