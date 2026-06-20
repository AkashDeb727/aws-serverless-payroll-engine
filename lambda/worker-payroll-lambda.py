import json
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError

lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

salary_table = dynamodb.Table('salary_components')
deduction_table = dynamodb.Table('deductions')
payroll_table = dynamodb.Table('payroll_runs')


def lambda_handler(event, context):

    for record in event['Records']:

        message = json.loads(record['body'])

        run_id = message['run_id']
        employee_id = message['employee_id']
        month = message['month']

        # Get salary data
        salary = salary_table.get_item(
            Key={'employee_id': employee_id}
        )

        salary_item = salary['Item']

        basic = float(salary_item['basic_salary'])
        hra = float(salary_item['hra'])
        transport = float(salary_item['transport_allowance'])
        custom = float(salary_item['custom_allowance'])

        # Get deductions
        deduction = deduction_table.get_item(
            Key={'employee_id': employee_id}
        )

        deduction_item = deduction['Item']

        pf = float(deduction_item['pf'])
        pt = float(deduction_item['professional_tax'])
        tds = float(deduction_item['tds'])
        loan = float(deduction_item['loan_deduction'])

        gross = basic + hra + transport + custom

        deductions_total = pf + pt + tds + loan

        net_pay = gross - deductions_total

        try:

            payroll_table.put_item(
                Item={
                    'run_id': run_id,
                    'employee_id': employee_id,
                    'month': month,
                    'gross': Decimal(str(gross)),
                    'deductions_total': Decimal(str(deductions_total)),
                    'net_pay': Decimal(str(net_pay)),
                    'status': 'PROCESSING'
                },
                ConditionExpression='attribute_not_exists(run_id) AND attribute_not_exists(employee_id)'
            )

            print(
                f"Processed {employee_id} | Net Pay = {net_pay}"
            )

            payload = {
                "run_id": run_id,

                "employee_name": salary_item["employee_name"],
                "employee_email": salary_item["email"],
                "employee_id": employee_id,
                "month": month,

                "basic": basic,
                "hra": hra,
                "transport": transport,
                "custom": custom,

                "pf": pf,
                "professional_tax": pt,
                "tds": tds,
                "loan": loan,

                "gross": gross,
                "deductions_total": deductions_total,
                "net_pay": net_pay
            }

            response = lambda_client.invoke(
                FunctionName='pdf-generator-lambda',
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

        except ClientError as e:

            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':

                print(
                    f"Duplicate payroll detected for {employee_id}. Skipping."
                )

                continue

            raise e

    return {
        'statusCode': 200
    }