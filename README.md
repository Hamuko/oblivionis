# oblivionis

Discord bot for tracking gameplay time.

## Usage

### Docker Compose

```yaml
version: '3.7'
services:
  oblivionis:
    image: ghcr.io/hamuko/oblivionis:latest
    container_name: oblivionis
    environment:
      - DB_HOST=postgres
      - DB_NAME=oblivionis
      - DB_PASSWORD=postgres-secret
      - DB_USER=oblivionis
      - TOKEN=discord-secret
    restart: on-failure
```

