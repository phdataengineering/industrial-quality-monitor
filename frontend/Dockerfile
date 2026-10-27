FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/app.py ./app.py
RUN useradd --create-home --uid 10002 streamlit-user \
    && chown -R streamlit-user:streamlit-user /app
USER streamlit-user
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--server.enableCORS=true", "--server.enableXsrfProtection=true", "--browser.gatherUsageStats=false"]
