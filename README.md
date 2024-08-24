# suomiahven
An extendable Finnish Discord bot. 

## Currently implemented extensions (cogs)
    - ping (in-progress)
    - greeter (in-progress)
    - music (in-progress)
    - help (in-progress)
    - template (reference)

## Dependencies
* Core
    - discord.py
    - python-dotenv
* Music cog
    - yt-dlp
    - pyttsx3
    - pydub
    - PyNaCl

## Running the bot

### 1. Running the bot natively:
Run the `run.py` installer or install the files via `pip3 install -r requirements.txt` and execute the `main.py` directly.

### 2. Running the bot using Docker:

#### Step 1: Build the Docker image

First, make sure you have Docker installed on your machine. Then, navigate to the project directory and run the following command to build the Docker image:

```bash
docker build -t suomiahven .
This command will create a Docker image named suomiahven based on the Dockerfile provided in the project.
Step 2: Create and configure the .env file

The bot requires a .env file to run, which should contain your Discord bot token and the path to FFMPEG. Create a .env file in the project root directory with the following content:

DISCORD_BOT_TOKEN=your_discord_bot_token
FFMPEG_PATH=/usr/bin/ffmpeg

Replace your_discord_bot_token with your actual Discord bot token.
Step 3: Run the Docker container

Once the Docker image is built and the .env file is configured, you can run the bot using the following command:
docker run -it --rm --env-file .env suomiahven

This command will start a Docker container using the suomiahven image and pass in the environment variables from the .env file. The bot will then start running inside the container.
Notes:

    Environment Variables: Make sure your .env file is correctly configured with the necessary environment variables, especially your Discord bot token.
    Docker Clean-up: The --rm flag in the docker run command ensures that the container is removed after it stops. This is useful for keeping your system clean.

Now, you can use Docker to easily run and manage the suomiahven Discord bot!