FROM python:3.7.4-slim-stretch

ENV PYTHONPATH=/evaluation_system/
ENV GOOGLE_APPLICATION_CREDENTIALS=/evaluation_system/ev_sys_pwa/service.json

COPY . ${PYTHONPATH}ev_sys_pwa/

RUN apt-get update \
    && apt-get install -y apt-utils g++ default-libmysqlclient-dev libeccodes-dev \
    && apt-get install -y tzdata \
    && cp -f /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ${PYTHONPATH}ev_sys_pwa/requirements.txt \
    && apt-get clean \
    && rm -rf /var/cache/apk/* \
    && mkdir -p /var/log/nrgp

WORKDIR ${PYTHONPATH}
RUN ${PYTHONPATH}ev_sys_pwa/manage.py collectstatic --no-input

CMD ["uwsgi","--ini","ev_sys_pwa/api/uwsgi.ini","--static-map","/static=collected_static"]
