import json
import boto3
import uuid
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

table = dynamodb.Table(os.environ['TABLE_NAME'])
queue_url = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):

    run_id = str(uuid.uuid4())

    month = datetime.now().strftime("%Y-%m")

    response = table.scan()

    employees = response['Items']

    for employee in employees:

        message = {
            "run_id": run_id,
            "employee_id": employee['employee_id'],
            "month": month
        }

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "run_id": run_id,
            "employees_processed": len(employees)
        })
    }