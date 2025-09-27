# suomiahven

An extendable Finnish Discord bot.

## Currently implemented extensions (cogs)

* ping (in-progress)
* greeter (in-progress)
* music (in-progress)
* help (in-progress)
* template (reference)

## Dependencies

* Core

  * discord.py
  * python-dotenv
* Music cog

  * yt-dlp
  * pyttsx3
  * pydub
  * PyNaCl

## Running the bot

### 1. Running the bot natively:

Run the `run.py` installer or install the files via `pip3 install -r requirements.txt` and execute the `main.py` directly.

### 2. Running the bot using Docker

#### Step 1: Build the Docker image

Make sure Docker is installed. From the project root, build the image:

```bash
docker build -t suomiahven .
```

This creates a Docker image named `suomiahven` based on the provided `Dockerfile`.

#### Step 2: Create and configure the `.env` file

Create a `.env` file in the project root containing your Discord bot token (and optional settings like FFMPEG path):

```dotenv
DISCORD_BOT_TOKEN=your_discord_bot_token
FFMPEG_PATH=/usr/bin/ffmpeg
```

Replace `your_discord_bot_token` with your actual token.

#### Step 3a: Run the container manually

```bash
docker run -it --rm --env-file .env suomiahven
```

This starts a container using the `suomiahven` image and passes environment variables from `.env`.

#### Step 3b: Run the bot using Docker Compose (minimal, no persistent data/logs)

Create `docker-compose.yml` in the project root with:

```yaml
services:
  suomiahven:
    build: .
    container_name: suomiahven
    env_file:
      - .env
    environment:
      - FFMPEG_PATH=/usr/bin/ffmpeg
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Start/stop with:

```bash
# build (if needed) and start in background
docker compose up -d --build

# view logs
docker compose logs -f

# stop and remove containers/networks
docker compose down
```

### Notes

* Ensure `.env` is correctly configured (especially `DISCORD_BOT_TOKEN`).
* With `docker run`, the `--rm` flag removes the container on exit. With Compose, use `docker compose down` to clean up.
* If you later add persistent data or logs, mount volumes in Compose (e.g., `./data:/app/data`, `./logs:/app/logs`).
