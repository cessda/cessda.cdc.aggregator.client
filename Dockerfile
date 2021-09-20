# syntax=docker/dockerfile:1
#
# Updated dockerfile syntax is required for --mount option
#
# Declares a two-stage build that initially builds all python
# packages and installs them into .local in the first stage.
# Then use another stage to actually create the image without
# temporary files or git by copying .local from first stage
# and prepending it to PATH.
#
#
#
# Building the image
# ##################
#
# The build needs credentials to access Bitbucket. It uses
# --secret option, which is a feature provided by buildkit.
# The secret is expected to be accessible within the build-
# container via id 'bbcreds'. See buildkit manual on how to
# pass the secret to the build.
#
# Example with a mysecret-file:
#
# $ echo bbhandle:passw0rd > mysecret
# $ DOCKER_BUILDKIT=1 docker build \
#     -t "cdcagg-client" \
#     --secret id=bbcreds,src=mysecret .
#
#
#
# Running the container
# #####################
#
# The application needs two mounts in order to operate properly:
#
# * /xml_sources is an external volume and should be mounted
#   as read-only when starting the container.
#
# * /app_data is used to store sourcefile modification
#   timestamps to reduce resource on subsequent runs. It should
#   be mounted with write-permissions.
#
# Document Store URL must also be configured. Operator may use
# environment variable CDCAGG_DS_URL to configure the URL.
#
# Example command to run the container:
#
# $ docker run \
#     --name "cdcagg_client" \
#     --mount source=xml_sources,destination=/xml_sources,readonly \
#     --mount source=app_data,destination=/app_data \
#     -e "CDCAGG_DS_URL=http://153.1.61.18:5001/v0" \
#     cdcagg-client
#

FROM python:3.9-slim as builder

COPY . /docker-build
WORKDIR /docker-build

RUN apt-get update \
  && apt-get install git -y \
  && apt-get clean

# Expects 'bbcreds'-secret.

RUN --mount=type=secret,id=bbcreds \
  BBCREDS=$(cat /run/secrets/bbcreds) \
  pip install --user -r requirements.txt \
  && pip install --user .


# END FIRST STAGE


FROM python:3.9-slim as prod

# Copy build packages from builder image to prod.
# Add them to PATH.

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

VOLUME ["/app_data"]

CMD ["--file-cache", "/app_data/file_cache.pickle", "/xml_sources"]

ENTRYPOINT ["python", "-m", "cdcagg_client.sync"]

# END SECOND STAGE
