FROM python:3.5-onbuild
MAINTAINER Johannes Innerbichler <j.innerbichler@gmail.com>

ENV PYTHONPATH .
ENTRYPOINT ["python", "manage.py"]