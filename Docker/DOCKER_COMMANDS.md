# Comprehensive Docker & Docker Compose Cheatsheet

This reference document covers the core standalone **Docker CLI** commands, **Docker Compose** commands, **Dockerfile** directives, port mapping rules, and key lessons learned throughout this DevOps lab.

---

## 1. Core Docker CLI Commands

### A. Building & Tagging Images

| Command | Description | Example |
| :--- | :--- | :--- |
| `docker build` | Builds a Docker image from a Dockerfile in the specified path. | `docker build -t my-flask-app .` |
| `docker build -t <name>:<tag> .` | Builds and tags an image with a specific name and tag. | `docker build -t my-flask-app:v1.0 .` |
| `docker build -f <file> .` | Builds an image using a custom Dockerfile path. | `docker build -f Dockerfile.dev -t my-app:dev .` |
| `docker tag <source> <target>` | Creates a new tag that refers to an existing image. | `docker tag my-flask-app:v1.0 myusername/my-flask-app:latest` |
| `docker images` | Lists all locally available Docker images. | `docker images` |
| `docker rmi <image_id>` | Removes one or more local images by ID or name. | `docker rmi my-flask-app:v1.0` |
| `docker pull <image>` | Pulls an image from Docker Hub or a remote registry. | `docker pull redis:alpine` |
| `docker push <image>` | Pushes a tagged image to Docker Hub or remote registry. | `docker push myusername/my-flask-app:latest` |

---

### B. Running Containers (`docker run`)

`docker run` creates and starts a container from an image.

```powershell
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

#### Common `docker run` Flags:
- `-d` : Run container in background (detached mode).
- `-p <host_port>:<container_port>` : Publish / map container port to host port.
- `--name <name>` : Assign a custom, memorable name to the container.
- `-e <KEY=VALUE>` : Set runtime environment variables inside the container.
- `-v <host_path>:<container_path>` : Mount a volume or host directory into the container.
- `--rm` : Automatically remove the container when it exits/stops.
- `-it` : Run interactively with a pseudo-TTY attached (terminal access).

#### Practical Examples:
```powershell
# 1. Run Flask app in background with port mapping and a custom name:
docker run -d -p 8000:5000 --name web-container my-flask-app

# 2. Run Redis in background:
docker run -d --name redis-server -p 6379:6379 redis:alpine

# 3. Run container and pass environment variables:
docker run -d -p 8000:5000 -e REDIS_HOST=redis -e REDIS_PORT=6379 my-flask-app

# 4. Run an interactive shell in an alpine container and remove it on exit:
docker run --rm -it alpine sh
```

---

### C. Viewing & Managing Running Containers (`docker ps`)

| Command | Description |
| :--- | :--- |
| `docker ps` | Lists all **currently running** containers. Shows Container ID, Image, Command, Created time, Status, Ports, and Names. |
| `docker ps -a` | Lists **all** containers, including stopped, exited, and failed ones. Essential for debugging crashed containers. |
| `docker ps -q` | Lists only container IDs (useful for piping into scripts). |
| `docker stop <container>` | Gracefully stops a running container. |
| `docker start <container>` | Starts an existing stopped container. |
| `docker restart <container>` | Restarts a running container. |
| `docker rm <container>` | Deletes a stopped container. |
| `docker rm -f <container>` | Forces removal of a container (even if currently running). |

---

### D. Logs & Inspection

| Command | Description | Example |
| :--- | :--- | :--- |
| `docker logs <container>` | Displays all logs output by the container to STDOUT / STDERR. | `docker logs web-container` |
| `docker logs -f <container>` | Follows (tails) live logs in real time as they arrive. | `docker logs -f web-container` |
| `docker logs --tail <n> <container>` | Shows only the last `n` lines of logs. | `docker logs --tail 50 web-container` |
| `docker logs -t <container>` | Prepends timestamps to every log line. | `docker logs -t -f web-container` |
| `docker inspect <container>` | Returns low-level configuration, network settings, and IP details in JSON format. | `docker inspect web-container` |

---

### E. Executing Commands Inside Containers

| Command | Description | Example |
| :--- | :--- | :--- |
| `docker exec -it <container> <shell>` | Opens an interactive shell session inside an active container. | `docker exec -it web-container sh`<br>`docker exec -it redis-server redis-cli` |
| `docker exec <container> <command>` | Runs a one-off command inside the container without entering a shell. | `docker exec web-container env` |

---

### F. Housekeeping & Cleanup

| Command | Description |
| :--- | :--- |
| `docker container prune` | Removes all stopped containers at once. |
| `docker image prune` | Removes all dangling (untagged) images. |
| `docker system prune` | Removes all unused containers, dangling images, and build cache. |
| `docker system prune -a --volumes` | Deep cleanup: removes all stopped containers, unused networks, all unused images, and all unused volumes. |

---

## 2. Docker Compose Commands

Docker Compose manages multi-container stacks defined in `docker-compose.yml`.

| Command | Description |
| :--- | :--- |
| `docker-compose up` | Builds (if needed), creates, and starts all services in the foreground. |
| `docker-compose up --build` | Forces rebuild of custom images before starting services. |
| `docker-compose up -d` | Runs all containers in detached mode (background). |
| `docker-compose down` | Stops and removes containers and internal networks created by `up`. |
| `docker-compose down -v` | Stops containers and removes named volumes (wiping persistent data). |
| `docker-compose build` | Builds or rebuilds service images without starting containers. |
| `docker-compose ps` | Lists status of containers defined in the current compose file. |
| `docker-compose logs` | Views output logs for all services in the compose stack. |
| `docker-compose logs -f web` | Follows real-time logs specifically for the `web` service. |
| `docker-compose stop` | Stops services without removing their containers. |
| `docker-compose start` | Starts stopped services. |
| `docker-compose restart` | Restarts all services in the compose stack. |
| `docker-compose exec web sh` | Opens a shell inside the running `web` service container. |

---

## 3. Deep Dive: Port Mapping Concept

Whether using `docker run -p` or `ports:` in `docker-compose.yml`, port mapping always follows:

$$\text{HOST\_PORT} : \text{CONTAINER\_PORT}$$

```text
       Browser (Host Machine)
       http://localhost:8000
                 │
                 ▼
      ┌─────────────────────┐
      │  Host Port: 8000    │
      └──────────┬──────────┘
                 │ (Forwarded by Docker)
                 ▼
      ┌─────────────────────┐
      │ Container Port: 5000│  <-- Flask app listens here inside container
      └─────────────────────┘
```

- **Host Port (`8000`)**: Port opened on your physical computer. This is what you type into your browser (`http://localhost:8000`).
- **Container Port (`5000`)**: Port the application listens to inside the isolated container environment.
- **Why `http://localhost:5000` refused to connect**: Flask was bound to internal container port 5000, but only exposed externally to host port 8000.

---

## 4. Dockerfile Directives Summary

| Directive | Purpose | Example |
| :--- | :--- | :--- |
| `FROM` | Sets base OS / runtime image | `FROM python:3.12-alpine` |
| `WORKDIR` | Sets active working directory inside container | `WORKDIR /app` |
| `ENV` | Sets environment variables | `ENV FLASK_APP=demo.py` |
| `RUN` | Runs commands at build-time (installs packages) | `RUN pip install -r requirements.txt` |
| `COPY` | Copies files from host to container (`<src> <dest>`) | `COPY python/demo.py demo.py` |
| `EXPOSE` | Documents intended port (informational) | `EXPOSE 5000` |
| `CMD` | Default command executed when container launches | `CMD ["flask", "run", "--debug"]` |

---

## 5. Key Pitfalls & Solutions

1. **`COPY` syntax error (`Destination could not be determined`)**:
   - `COPY` requires both source and destination: `COPY python/demo.py demo.py` (not just `COPY python/demo.py`).
2. **Container Networking**:
   - In Docker Compose, containers communicate using service names (e.g. `redis`) as hostnames on the shared network.
3. **IDE "Cannot find module" warnings (`flask`, `redis`)**:
   - Packages installed via Dockerfile exist inside the Linux container, not in the local host OS Python environment.
   - Run `pip install -r python/requirements.txt` locally if you want editor autocompletion and no lint errors.
