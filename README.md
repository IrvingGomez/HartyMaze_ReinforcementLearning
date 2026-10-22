# Harty's Maze (01_GridWorld)

A reinforcement learning lesson for high-school students. Students build a maze, press Run, and Harty teaches policy iteration on it, step by step.

The whole app is one file, `harty-maze-builder.html`. It needs no server and no internet: double-click it to open it.

## Run with Docker

```bash
docker compose up -d --build     # then open http://localhost:8080
docker compose down              # stop it
```

Without Compose:

```bash
docker build -t harty-maze .
docker run -d --name harty-maze -p 8080:8080 --restart unless-stopped harty-maze
```

The image is nginx serving the HTML file as `index.html`, running as a non-root user on port 8080. A health check answers at `/healthz`.

### Deploying on the university server

- Put a reverse proxy (or the server's existing gateway) in front of port 8080 for HTTPS and the final URL.
- To serve under a sub-path such as `/harty/`, proxy that path to the container and strip the prefix. The app uses no absolute URLs, so nothing else needs changing.
- To update after editing the HTML: `git pull && docker compose up -d --build`.
