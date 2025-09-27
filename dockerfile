# Käytetään Python 3.11 pohjakuvana
FROM python:3.11-slim

# Ympäristömuuttujat: ei .pyc-tiedostoja ja välitön lokitus
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FFMPEG_PATH=/usr/bin/ffmpeg

# Työhakemisto
WORKDIR /app

# Järjestelmäriippuvuudet (ffmpeg + varmenteet)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Kopioi riippuvuudet ensin (parempi layer-cache)
COPY requirements.txt /app/requirements.txt

# Perusasennus (build-vaiheessa)
RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r /app/requirements.txt

# Kopioi lähdekoodi ja entrypoint
COPY . /app

# Oletuskomento: Python-entrypoint hoitaa päivitykset ja botin ajon
CMD ["python", "entrypoint.py"]
