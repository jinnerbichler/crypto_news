FROM python:3.5
MAINTAINER Johannes Innerbichler <j.innerbichler@gmail.com>

ENV PYTHONPATH .
ENTRYPOINT ["python", "manage.py"]