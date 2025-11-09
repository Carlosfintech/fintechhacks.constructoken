FROM ghcr.io/br3ndonland/inboard:fastapi-0.72.2-python3.12

# Use file.name* in case it doesn't exist in the repo
COPY ./app/ /app/
WORKDIR /app/
ENV \
  PYTHONUNBUFFERED=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_CONCURRENT_INSTALLS=1 \
  UV_LINK_MODE=copy \
  HATCH_ENV_TYPE_VIRTUAL_PATH=.venv
# If installing Jupyter - or in Development mode - then install the development environment, else production
# For using the Jupyter remote kernel inside the container - or the environment variable `JUPYTER`:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
# Add new production or development dependencies to the appropriate spots in `pyproject.toml`
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then hatch env prune && hatch env create development && pip install --upgrade setuptools ; else hatch env prune && hatch env create production && pip install --upgrade setuptools ; fi"
# RUN bash -c "pip install argon2_cffi"

# /start Project-specific dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*	
# WORKDIR /app/
# /end Project-specific dependencies

ARG BACKEND_APP_MODULE=app.main:app
ARG BACKEND_PRE_START_PATH=/app/scripts/prestart.sh
ARG BACKEND_PROCESS_MANAGER=gunicorn
ARG BACKEND_WITH_RELOAD=false
ENV APP_MODULE=${BACKEND_APP_MODULE} PRE_START_PATH=${BACKEND_PRE_START_PATH} PROCESS_MANAGER=${BACKEND_PROCESS_MANAGER} WITH_RELOAD=${BACKEND_WITH_RELOAD}