# AWS Serverless Payroll Processing & Payslip Delivery Engine

A cloud-native payroll automation platform built using AWS serverless services to automate payroll execution, salary calculations, PDF payslip generation, secure storage, and employee email delivery.

The solution leverages AWS Lambda, Amazon SQS, DynamoDB, Amazon S3, Amazon SES, and API Gateway to create a scalable, event-driven payroll processing system while implementing idempotency safeguards to prevent duplicate payroll execution.

---

# Architecture Diagram

![Architecture Diagram](architecture/architecture-diagram.png)

---

# Project Overview

This project was developed as a complete end-to-end payroll processing solution on AWS.

The system enables HR teams to trigger payroll runs, automatically process employee salaries and deductions, generate professional PDF payslips, securely store them in Amazon S3, and deliver them to employees via Amazon SES.

The architecture follows modern serverless design principles, eliminating infrastructure management while ensuring scalability, reliability, and fault tolerance.

---

# Key Features

* Automated payroll execution
* Event-driven serverless architecture
* Amazon SQS fan-out processing
* Payroll calculation engine
* PDF payslip generation
* Secure storage using Amazon S3
* Pre-signed URL generation
* Email delivery through Amazon SES
* Idempotent payroll processing
* HR Dashboard for payroll monitoring
* CSV export functionality
* Cloud-native architecture

---

# AWS Services Used

| Service            | Purpose                              |
| ------------------ | ------------------------------------ |
| AWS Lambda         | Payroll orchestration and processing |
| Amazon SQS         | Asynchronous message queue           |
| Amazon DynamoDB    | Employee and payroll data storage    |
| Amazon S3          | Payslip storage                      |
| Amazon SES         | Employee email delivery              |
| Amazon API Gateway | Payroll execution endpoint           |
| AWS IAM            | Authentication and access control    |
| Amazon CloudWatch  | Monitoring and logging               |

---

# System Architecture

```text
API Gateway
      │
      ▼
Trigger Payroll Lambda
      │
      ▼
Amazon SQS (Payroll Queue)
      │
      ▼
Worker Payroll Lambda
      │
      ▼
Amazon DynamoDB
      │
      ▼
PDF Generator Lambda
      │
      ▼
Amazon S3
      │
      ▼
Email Delivery Lambda
      │
      ▼
Employee Email
```

---

# Payroll Processing Workflow

## Step 1 – Payroll Trigger

An HR user initiates a payroll run through API Gateway.

The Trigger Payroll Lambda:

* Reads employee records from DynamoDB
* Generates a unique payroll run identifier
* Sends one message per employee to Amazon SQS

---

## Step 2 – Payroll Calculation

The Worker Payroll Lambda processes messages from Amazon SQS.

For each employee:

* Retrieves salary information
* Retrieves deduction information
* Calculates gross salary
* Calculates total deductions
* Calculates net salary
* Stores payroll results in DynamoDB

---

## Step 3 – Payslip Generation

The PDF Generator Lambda:

* Generates a professional PDF payslip
* Uploads the payslip to Amazon S3
* Creates a secure pre-signed URL

---

## Step 4 – Employee Notification

The Email Delivery Lambda:

* Retrieves employee email information
* Sends payroll notifications using Amazon SES
* Includes secure payslip access links

---

# DynamoDB Data Model

## salary_components

Stores employee salary information:

* Employee ID
* Employee Name
* Employee Email
* Basic Salary
* HRA
* Transport Allowance
* Custom Allowance

---

## deductions

Stores employee deduction information:

* Provident Fund (PF)
* Professional Tax
* TDS
* Loan Deductions

---

## payroll_runs

Stores payroll execution results:

* Run ID
* Employee ID
* Payroll Month
* Gross Salary
* Total Deductions
* Net Salary
* Processing Status
* Payslip S3 Location

---

# Idempotency Implementation

Payroll systems require strict protection against duplicate processing.

To ensure reliable execution, the project implements idempotency using a unique combination of:

```text
run_id + employee_id
```

Before processing payroll data, the system verifies whether the employee has already been processed for the current payroll run.

If a matching record already exists, processing is skipped.

This prevents:

* Duplicate payroll calculations
* Duplicate payslip generation
* Duplicate employee payments
* Errors caused by Lambda retries

Additional details can be found in:

```text
docs/Idempotency-Explanation.pdf
```

---

# Repository Structure

```text
aws-serverless-payroll-engine
│
├── architecture/
│   └── architecture-diagram.png
│
├── dashboard/
│   └── payroll-dashboard.html
│
├── docs/
│   └── Idempotency-Explanation.pdf
│
├── lambda/
│   ├── trigger-payroll-lambda.py
│   ├── worker-payroll-lambda.py
│   ├── pdf-generator-lambda.py
│   ├── email-delivery-lambda.py
│   └── get-payroll-runs-lambda.py
│
├── screenshots/
│   ├── dashboard/
│   ├── infrastructure/
│   └── outputs/
│
├── README.md
└── .gitignore
```

---

# Project Screenshots

## Dashboard

Contains payroll execution and monitoring screenshots.

```text
screenshots/dashboard/
```

---

## Infrastructure

Contains AWS infrastructure screenshots including:

* API Gateway
* Lambda Functions
* DynamoDB Tables
* SQS Queue
* Amazon S3

```text
screenshots/infrastructure/
```

---

## Outputs

Contains generated project outputs including:

* Generated PDF Payslip
* Payroll Processing Records
* SES Email Delivery
* Payroll CSV Export

```text
screenshots/outputs/
```

---

# Team Contributions

## Akash Deb

* DynamoDB data modeling
* Amazon SQS integration
* Trigger Payroll Lambda
* Worker Payroll Lambda
* Payroll calculation engine
* Idempotency implementation
* Architecture Diagram
* HR Dashboard development

---

## Ibrahim Ajmeri

* ReportLab integration
* PDF Generator Lambda
* Amazon S3 integration
* Pre-signed URL generation

---

## Rushi Sanku

* Amazon SES integration
* Email Delivery Lambda
* CSV Export functionality

---

# Project Outcome

Successfully designed, developed, and demonstrated a complete serverless payroll processing platform capable of:

* Processing payroll for multiple employees
* Generating professional PDF payslips
* Securely storing payroll documents
* Delivering payslips through Amazon SES
* Exporting payroll records in CSV format
* Preventing duplicate payroll execution through idempotent processing
* Providing payroll visibility through an HR dashboard

This project demonstrates practical implementation of AWS serverless services, event-driven architecture, asynchronous processing, secure document delivery, cloud storage, and scalable payroll automation in a real-world business use case.
