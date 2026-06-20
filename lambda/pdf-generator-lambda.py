import json
import boto3
from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")

BUCKET_NAME = "payroll-payslips-ibrahim"

payroll_table = dynamodb.Table("payroll_runs")


def lambda_handler(event, context):

    run_id = event["run_id"]

    employee_name = event["employee_name"]
    employee_email = event["employee_email"]
    employee_id = event["employee_id"]
    month = event["month"]

    basic = float(event["basic"])
    hra = float(event["hra"])
    transport = float(event["transport"])
    custom = float(event["custom"])

    pf = float(event["pf"])
    professional_tax = float(event["professional_tax"])
    tds = float(event["tds"])
    loan = float(event["loan"])

    gross = float(event["gross"])
    deductions_total = float(event["deductions_total"])
    net_pay = float(event["net_pay"])

    year = month.split("-")[0]
    month_number = month.split("-")[1]

    month_names = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

    display_month = f"{month_names.get(month_number, month_number)} {year}"

    pdf_buffer = BytesIO()

    doc = SimpleDocTemplate(pdf_buffer)

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    title_style.fontSize = 24

    footer_style = styles["Normal"]
    footer_style.alignment = TA_CENTER

    elements = []

    # PAYSLIP TITLE

    elements.append(
        Paragraph(
            "PAYSLIP",
            title_style
        )
    )

    elements.append(Spacer(1, 20))

    # EMPLOYEE DETAILS

    employee_data = [
        ["Employee Name", employee_name],
        ["Employee ID", employee_id],
        ["Payroll Month", display_month]
    ]

    employee_table = Table(
        employee_data,
        colWidths=[180, 220]
    )

    employee_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold")
        ])
    )

    elements.append(employee_table)

    elements.append(Spacer(1, 20))

    # EARNINGS

    elements.append(
        Paragraph(
            "<b>EARNINGS</b>",
            styles["Heading3"]
        )
    )

    earnings_data = [
        ["Description", "Amount (Rs.)"],
        ["Basic Salary", f"{basic:,.2f}"],
        ["HRA", f"{hra:,.2f}"],
        ["Transport Allowance", f"{transport:,.2f}"],
        ["Custom Allowance", f"{custom:,.2f}"],
        ["Gross Salary", f"{gross:,.2f}"]
    ]

    earnings_table = Table(
        earnings_data,
        colWidths=[250, 150]
    )

    earnings_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold")
        ])
    )

    elements.append(earnings_table)

    elements.append(Spacer(1, 20))

    # DEDUCTIONS

    elements.append(
        Paragraph(
            "<b>DEDUCTIONS</b>",
            styles["Heading3"]
        )
    )

    deductions_data = [
        ["Description", "Amount (Rs.)"],
        ["PF", f"{pf:,.2f}"],
        ["Professional Tax", f"{professional_tax:,.2f}"],
        ["TDS", f"{tds:,.2f}"],
        ["Loan Deduction", f"{loan:,.2f}"],
        ["Total Deductions", f"{deductions_total:,.2f}"]
    ]

    deductions_table = Table(
        deductions_data,
        colWidths=[250, 150]
    )

    deductions_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold")
        ])
    )

    elements.append(deductions_table)

    elements.append(Spacer(1, 20))

    # NET PAY

    net_pay_data = [
        ["NET PAY", f"Rs. {net_pay:,.2f}"]
    ]

    net_pay_table = Table(
        net_pay_data,
        colWidths=[200, 200]
    )

    net_pay_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.lightgreen),
            ("GRID", (0, 0), (-1, -1), 2, colors.black),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 14)
        ])
    )

    elements.append(net_pay_table)

    elements.append(Spacer(1, 25))

    # FOOTER

    elements.append(
        Paragraph(
            "<i>This is a system generated payslip.</i>",
            footer_style
        )
    )

    doc.build(elements)

    pdf_buffer.seek(0)

    s3_key = f"payslips/{year}/{month_number}/{employee_id}.pdf"

    s3.upload_fileobj(
        pdf_buffer,
        BUCKET_NAME,
        s3_key,
        ExtraArgs={
            "ContentType": "application/pdf"
        }
    )

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": s3_key
        },
        ExpiresIn=604800
    )

    payroll_table.update_item(
        Key={
            "run_id": run_id,
            "employee_id": employee_id
        },
        UpdateExpression="""
            SET #status = :done,
                payslip_s3_key = :s3key,
                presigned_url = :url
        """,
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":done": "DONE",
            ":s3key": s3_key,
            ":url": url
        }
    )

    print(
        f"EMPLOYEE={employee_id} EMAIL={employee_email}"
    )

    email_payload = {
        "email": employee_email,
        "name": employee_name,
        "pdf_url": url,
        "month": display_month
    }

    response = lambda_client.invoke(
        FunctionName="email-delivery-lambda",
        InvocationType="Event",
        Payload=json.dumps(email_payload)
    )

    print(response)

    print(
        f"Payslip generated and email triggered for {employee_name}"
    )

    return {
        "statusCode": 200,
        "pdf_url": url,
        "s3_key": s3_key
    }