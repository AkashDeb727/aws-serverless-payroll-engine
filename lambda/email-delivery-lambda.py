import json
import boto3

ses = boto3.client(
    'ses',
    region_name='ap-south-1'
)

SENDER = "2403A51028@sru.edu.in"

def lambda_handler(event, context):

    recipient = event["email"]
    employee_name = event["name"]
    pdf_url = event["pdf_url"]
    month = event["month"]

    print(json.dumps(event))

    response = ses.send_email(
        Source=SENDER,
        Destination={
            'ToAddresses': [recipient]
        },
        Message={
            'Subject': {
                'Data': f'Your Payslip for {month} is Ready'
            },
            'Body': {
                'Text': {
                    'Data': f'''
Hello {employee_name},

Your payroll for {month} has been processed successfully.

You can download your payslip using the secure link below:

{pdf_url}

Note:
This pre-signed URL will expire in 7 days.

Regards,
Payroll Team
'''
                }
            }
        }
    )

    print(
        f"Email sent successfully to {recipient}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Email sent successfully",
            "messageId": response["MessageId"]
        })
    }