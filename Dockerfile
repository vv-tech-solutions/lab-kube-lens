# Utilisation d'une image de base légère et compatible multi-arch
FROM python:3.12-slim

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-root pour la sécurité sur K8s
RUN useradd --create-home appuser
USER appuser
WORKDIR /app

# Installation des dépendances
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copie du code source
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser pyproject.toml .

# Installation du package local
RUN pip install --no-cache-dir --user --no-deps .

EXPOSE 8000

# Utilisation de la forme exec pour le signal handling (SIGTERM)
CMD ["python", "-m", "app.server"]