FROM python:3.7.4-slim-stretch

ENV PYTHONPATH=/evaluation_system/
ENV GOOGLE_APPLICATION_CREDENTIALS=/evaluation_system/evaluation_system/service.json

COPY . ${PYTHONPATH}evaluation_system/

RUN apt-get update \
    && apt-get install -y apt-utils g++ default-libmysqlclient-dev libeccodes-dev \
    && apt-get install -y tzdata \
    && cp -f /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ${PYTHONPATH}evaluation_system/requirements.txt \
    && apt-get clean \
    && rm -rf /var/cache/apk/* \
    && mkdir -p /var/log/nrgp

WORKDIR ${PYTHONPATH}
RUN ${PYTHONPATH}evaluation_system/manage.py collectstatic --no-input

CMD ["uwsgi","--ini","evaluation_system/api/uwsgi.ini","--static-map","/static=collected_static"]
