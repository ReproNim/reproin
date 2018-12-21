FROM nipy/heudiconv:latest

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends cron \
    && apt-get clean

COPY heudicron /etc/cron.d/heudicron
COPY heudiconv.sh start-cron /

RUN chmod +x /heudiconv.sh /start-cron \
    && chmod 0644 /etc/cron.d/heudicron \
    && touch /var/log/cron.log

ENTRYPOINT ["/start-cron"]
