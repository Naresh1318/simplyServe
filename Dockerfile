FROM python:3.6

# Need to install uWSGI
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install pigz

ADD requirements.txt /tmp/requirements.txt
RUN pip install --trusted-host pypi.python.org -r /tmp/requirements.txt

WORKDIR /simplyServe
COPY . /simplyServe

EXPOSE 5000

ENV SERVE_DIR "./temp"
ENV SERVER_NAME "simplyServe"
ENV ADMIN_EMAIL "a@1.com"
ENV ADMIN_PASS "test"
ENV ADMIN_NAME "admin"

CMD ["uwsgi", "--ini", "simplyServe.ini"]
