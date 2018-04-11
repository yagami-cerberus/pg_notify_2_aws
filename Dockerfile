FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip

ADD . /opt/pg_notify_2_aws
RUN pip3 install -r /opt/pg_notify_2_aws/requirements.txt

STOPSIGNAL 1

WORKDIR /opt/pg_notify_2_aws
CMD ["/opt/pg_notify_2_aws/pg_notify_2_aws.py"]
