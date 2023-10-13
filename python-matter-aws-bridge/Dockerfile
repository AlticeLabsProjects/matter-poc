# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

ENV WS_HOST=127.0.0.1
ENV WS_PORT=5580
ENV AWS_IOT_ENDPOINT=a2qzw5m91hzbht-ats.iot.eu-west-3.amazonaws.com
ENV AWS_API_URL=https://9oro4aipol.execute-api.eu-west-3.amazonaws.com/Prod/home/onboard/claim
ENV AWS_TEMPLATE_NAME=MatterProvisioningTemplate
ENV FGW_HOST=192.168.1.254
ENV FGW_PORT=80

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=chip_clusters-0.0-py3-none-any.whl,target=chip_clusters-0.0-py3-none-any.whl \
    python -m pip install ./chip_clusters-0.0-py3-none-any.whl

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Run the application.
CMD python3 -m main
