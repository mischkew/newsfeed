FROM python:3.9-alpine3.12

ARG period=daily

WORKDIR /app
COPY ["VERSION", "./setup.py", "README.md", "./"]
COPY "feed/" "feed/"
RUN pip install .

COPY "entrypoint.sh" "/etc/periodic/${period}/"
RUN mkdir /data/ && chmod +x "/etc/periodic/${period}/entrypoint.sh"

COPY "my-feeds.py" "./"

# make the build-arg period available for the command
ENV period=${period}
CMD "/etc/periodic/${period}/entrypoint.sh" && crond -f -d 6
