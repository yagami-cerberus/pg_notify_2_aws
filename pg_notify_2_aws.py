#!/usr/bin/env python3

from select import select
import urllib.parse
import os

import psycopg2.extensions
import psycopg2
import boto3


class AwsSqs(object):
    def __init__(self, queue_url):
        region_name = urllib.parse.urlparse(queue_url).netloc.split('.')[1]
        self.sqs = boto3.client('sqs', region_name=region_name)
        self.queue_url = queue_url

    def publish(self, pid, channel, payload):
        self.sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=payload,
            MessageAttributes={
                'service': {
                    'DataType': 'String',
                    'StringValue': 'pg_notify'
                },
                'pg_pid': {
                    'DataType': 'String',
                    'StringValue': str(pid)
                },
                'pg_channel': {
                    'DataType': 'String',
                    'StringValue': channel
                }
            })


class AwsSns(object):
    def __init__(self, topic_arn):
        region_name = topic_arn.split(':')[3]
        self.sns = boto3.client('sns', region_name=region_name)
        self.topic_arn = topic_arn

    def publish(self, pid, channel, payload):
        self.sns.publish(
            Message=payload,
            TopicArn=self.topic_arn,
            MessageAttributes={
                'service': {
                    'DataType': 'String',
                    'StringValue': 'pg_notify'
                },
                'pg_pid': {
                    'DataType': 'String',
                    'StringValue': str(pid)
                },
                'pg_channel': {
                    'DataType': 'String',
                    'StringValue': channel
                }
            })


def main():
    target = os.environ['TARGET']
    if target == 'sqs':
        aws = AwsSqs(os.environ['SQS_URL'])
    elif target == 'sns':
        aws = AwsSns(os.environ['SNS_TOPIC_ARN'])
    else:
        raise RuntimeError('Unknown arn %r, should be sns or sqs' % os.environ['TARGET_ARN'])

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    curs = conn.cursor()
    for channel in os.environ['PG_CHANNELS'].split(','):
        if channel:
            curs.execute("LISTEN %s;" % channel)

    select_args = ((conn, ), (), (), 30)
    while True:
        select(*select_args)
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            aws.publish(notify.pid, notify.channel, notify.payload)


if __name__ == '__main__':
    main()
