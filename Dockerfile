FROM python:3.12 AS build

RUN mkdir /src
WORKDIR /src

ADD requirements-deploy.txt /src
RUN pip install -r requirements-deploy.txt
ADD requirements.txt /src
RUN pip install -r requirements.txt

ADD README.md /src
ADD pyproject.toml /src

FROM build AS dev

VOLUME [ "/src" ]
WORKDIR /src

ADD requirements-dev.txt /src
RUN pip install -r requirements-dev.txt

ADD src /src/src
RUN pip install --editable .

ENV DJANGO_SETTINGS_MODULE ctlssa.app.settings

ENTRYPOINT [ "bash", "-c" ]
CMD [ "bash" ]

FROM build AS app

ADD src /src/src
RUN pip install --editable .

ENV DJANGO_SETTINGS_MODULE ctlssa.app.settings
ENV UWSGI_MODULE ctlssa.app.wsgi
ENV UWSGI_HTTP_SOCKET=:8001
ENV UWSGI_MASTER=1
ENV UWSGI_UID=nobody
ENV DJANGO_PORT=8001

EXPOSE 8001

ARG VERSION=0.0.0-dev0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=$VERSION

ENTRYPOINT [ "ctlssa" ]
