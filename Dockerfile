FROM python:3.12 AS build

RUN mkdir /src
WORKDIR /src

ADD requirements-deploy.txt /src
RUN pip install -r requirements-deploy.txt
ADD requirements.txt /src
RUN pip install -r requirements.txt

ADD README.md /src
ADD pyproject.toml /src
ADD src /src/src

RUN pip install .

FROM build AS dev

VOLUME [ "/src" ]
WORKDIR /src

ADD requirements-dev.txt /src
RUN pip install -r requirements-dev.txt

ENV DJANGO_SETTINGS_MODULE ctlssa.app.settings

ENTRYPOINT [ "bash", "-c" ]
CMD [ "bash" ]

FROM build AS app

ENV DJANGO_SETTINGS_MODULE ctlssa.app.settings
ENV UWSGI_MODULE ctlssa.app.wsgi
ENV UWSGI_HTTP_SOCKET=:8000
ENV UWSGI_MASTER=1
ENV UWSGI_UID=nobody

EXPOSE 8000

ARG VERSION=0.0.0-dev0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=$VERSION

ENTRYPOINT [ "ctlssa" ]
