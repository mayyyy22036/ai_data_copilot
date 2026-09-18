# Image de base légère (slim), suffisante pour FastAPI + les libs data/LLM
FROM python:3.11-slim

WORKDIR /app

# Copier requirements.txt SEUL d'abord : Docker met en cache cette étape.
# Tant que requirements.txt ne change pas, "pip install" n'est jamais
# ré-exécuté au prochain build, même si le code change — gain de temps énorme.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code seulement après (change beaucoup plus souvent)
COPY . .

# Cloud Run injecte automatiquement la variable PORT — on ne fixe jamais
# 8000 en dur dans la commande de démarrage, on lit ${PORT} avec 8000
# comme valeur par défaut pour le fonctionnement en local.
ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:'+__import__('os').environ.get('PORT','8000')+'/api/health')" || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
