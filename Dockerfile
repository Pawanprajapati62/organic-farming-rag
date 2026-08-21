FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN groupadd --system app && useradd --system --create-home --gid app app \
    && mkdir /app && chown app:app /app
RUN python -m pip install --no-cache-dir uv==0.12.5

WORKDIR /app
USER app

COPY --chown=app:app pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=app:app . .

USER root
RUN apt-get update \
    && apt-get install --no-install-recommends --yes gosu \
    && rm -rf /var/lib/apt/lists/*
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 755 /usr/local/bin/docker-entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["sh", "-c", "uv run --no-sync streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true"]
