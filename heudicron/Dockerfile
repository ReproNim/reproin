FROM nipy/heudiconv:latest

RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends cron \
    && apt-get clean

RUN git config --global user.email "user@heudiconv" \
    && git config --global user.name "heudiconv-erter"

COPY heudiconv.sh /

# save copy of current PATH to be used in cron job (hacky)
RUN echo ${PATH} > /opt/heudiconv.path

RUN chmod +x /heudiconv.sh \
    && (crontab -l; echo "* 4 * * * /heudiconv.sh > /proc/1/fd/1 2>/proc/1/fd/2") | crontab

ENTRYPOINT cron -f
