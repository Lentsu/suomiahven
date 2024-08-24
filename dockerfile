# Käytetään Python 3.11 pohjakuvana
FROM python:3.11-slim

# Määritellään työskentelyhakemisto
WORKDIR /app

# Asennetaan tarvittavat riippuvuudet, kuten FFMPEG
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Asennetaan tarvittavat Python-paketit
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Kopioidaan kaikki tiedostot projektihakemistoon
COPY . .

# Tarkistetaan, onko .env-tiedosto olemassa ja lisätään FFMPEG_PATH
RUN if [ -f .env ]; then \
        echo "\nFFMPEG_PATH=/usr/bin/ffmpeg" >> .env; \
    else \
        echo "FFMPEG_PATH=/usr/bin/ffmpeg" > .env; \
    fi

# Asetetaan oletuskomento kontille
CMD ["python", "main.py"]
