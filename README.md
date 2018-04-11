# PG Notify 2 AWS

Bypass postgres notify message to AWS SQS or SNS.


## Configuration

DATABASE_URL = `postgresql://pg_hostname/database`
TARGET=`sns`|`sqs`
PG_CHANNELS=`channel1,channel2`
SQS_URL=`https://sqs.us-west-1.amazonaws.com/0000000000/queue-name`
SNS_TOPIC_ARN=`arn:aws:sns:us-west-1:0000000000:topic-name`
