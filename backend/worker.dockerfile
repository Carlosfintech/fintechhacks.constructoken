FROM python:3.12
WORKDIR /app/
ARG \
  HATCH_VERSION=1.14.0 \
  PIPX_VERSION=1.7.1
ENV \
  C_FORCE_ROOT=1 \
  PYTHONUNBUFFERED=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_CONCURRENT_INSTALLS=1 \
  UV_LINK_MODE=copy \
  HATCH_ENV_TYPE_VIRTUAL_PATH=.venv \
  HATCH_VERSION=$HATCH_VERSION \
  PATH=/opt/pipx/bin:/app/.venv/bin:$PATH \
  PIPX_BIN_DIR=/opt/pipx/bin \
  PIPX_HOME=/opt/pipx/home \
  PIPX_VERSION=$PIPX_VERSION \
  PYTHONPATH=/app
COPY ./app/ /app/
RUN <<HEREDOC
python -m pip install --no-cache-dir --upgrade pip "pipx==$PIPX_VERSION"
pipx install "hatch==$HATCH_VERSION"
hatch env prune && hatch env create production
chmod +x /app/scripts/worker-start.sh
# /start Project-specific dependencies
# apt-get update && apt-get install -y --no-install-recommends
# rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# /end Project-specific dependencies
HEREDOC

CMD ["bash", "scripts/worker-start.sh"]
