<div align="center">

<img src="https://img.shields.io/badge/AWS-SSM_Parameter_Store-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white"/>
<img src="https://img.shields.io/badge/Amazon-EventBridge-E7157B?style=for-the-badge&logo=amazonaws&logoColor=white"/>
<img src="https://img.shields.io/badge/AWS-Lambda-FF9900?style=for-the-badge&logo=awslambda&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-boto3-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/DR-Disaster_Recovery-red?style=for-the-badge"/>

<br/><br/>

# 🔄 AWS SSM Cross-Region Sync & Drift Detection

**Event-driven configuration replication with automated drift detection for production ↔ DR parity**

`us-east-1 (prod)` &nbsp;→&nbsp; `us-east-2 (DR)`

</div>

---

## 📌 Overview

This project implements a robust **disaster recovery (DR) configuration management system** for AWS Systems Manager (SSM) Parameter Store. It ensures that parameters in the production region (`us-east-1`) are consistently synchronized and maintained in the DR region (`us-east-2`) using a combination of event-driven automation and drift detection.

---

## 🧩 Problem Statement

In multi-region architectures, **configuration drift** between production and DR environments can lead to failures during failover. Manual synchronization is inefficient and error-prone — especially for sensitive configurations like credentials and API keys.

---

## 🎯 Solution

This project provides a **hybrid approach** combining proactive real-time sync with reactive drift correction:

### ⚡ 1. Event-Driven Real-Time Synchronization

Captures parameter changes (Create / Update / Delete) in production, triggered automatically through the event pipeline:

- Amazon **EventBridge** detects SSM parameter change events
- Triggers an **AWS Lambda** function (`Lambda.py`) 
- Automatically:
  - Transforms parameter paths &nbsp;`/cln/prod/*` → `/cln/dr/*`
  - Applies environment-specific value updates
  - Replicates changes to the DR region

> 👉 Ensures **near real-time** consistency between regions

### 🔍 2. Drift Detection & Remediation

Compares parameters between `us-east-1 (/cln/prod/*)` and `us-east-2 (/cln/dr/*)`:

- Identifies **missing parameters** in DR
- Generates a structured **drift report (CSV)**
- Supports **bulk remediation** by recreating missing parameters

> 👉 Acts as a **fallback safety net** for configuration consistency

---

## 🏗️ Architecture

### Real-Time Sync Flow

```
SSM Parameter Change (Prod - us-east-1)
            │
            ▼
     EventBridge Rule
     (Captures SSM Events)
            │
            ▼
     Lambda Function
       (Lambda.py)
            │
            ▼
  Transform Parameter Path
  /cln/prod/* → /cln/dr/*
            │
            ▼
SSM Parameter Store (DR - us-east-2)
```

### Drift Detection Flow

```
Prod Parameters    →    Compare    →    DR Parameters
(us-east-1)          (check.py)         (us-east-2)
                           │
                           ▼
                    Generate Report
                      (check1.py)
                           │
                           ▼
                   Sync Missing Params
                     (createdr.py)
```

---

## 📁 Project Structure

```
ssm-cross-region-sync/
│
├── Lambda.py        # AWS Lambda handler — receives EventBridge events,
│                    # transforms paths, replicates parameters to DR region
│
├── check.py         # Drift detection — compares prod vs DR parameters,
│                    # identifies missing entries, outputs drift summary
│
├── check1.py        # Parameter export — fetches parameters with their
│                    # values from prod for analysis and reporting (CSV)
│
├── createdr.py      # Bulk remediation — recreates missing parameters
│                    # in DR region from the generated drift report
│
└── .gitignore       # Excludes secrets, CSVs, and environment files
```

---

## ⚙️ Tech Stack

### ☁️ AWS Services

| Service | Role |
|---|---|
| SSM Parameter Store | Configuration storage in both regions |
| Amazon EventBridge | Captures real-time SSM parameter change events |
| AWS Lambda | Processes events and replicates parameters to DR |
| AWS KMS | Encrypts / decrypts `SecureString` parameters cross-region |
| AWS IAM | Least-privilege access control |

### 💻 Tools & Languages

| Tool | Purpose |
|---|---|
| Python + boto3 | Core scripting and AWS SDK |
| AWS CLI | Manual testing and verification |
| Git & GitHub | Version control |

---

## 🔐 Security Considerations

- `SecureString` parameters are **decrypted securely** during processing and **re-encrypted using KMS** in the DR region
- **No secrets are stored** in the repository
- Sensitive files (CSVs, `.env`, credentials) are excluded via `.gitignore`
- All AWS access follows **least-privilege IAM** principles

---

## 🚀 Features

- ✅ Cross-region parameter replication
- ✅ Event-driven architecture (real-time sync)
- ✅ Drift detection and CSV reporting
- ✅ Bulk parameter creation in DR
- ✅ Secure handling of encrypted `SecureString` parameters
- ✅ Scalable and automation-ready design

---

## 🧪 Getting Started

### Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.9+ with `boto3` installed
- IAM permissions for the executing role/user:

```json
{
  "Action": [
    "ssm:GetParameter",
    "ssm:GetParametersByPath",
    "ssm:PutParameter",
    "ssm:DescribeParameters",
    "kms:Decrypt",
    "kms:Encrypt",
    "kms:GenerateDataKey"
  ]
}
```

### Install dependencies

```bash
pip install boto3
```

---

### 🔹 Run Drift Detection

Compares all parameters under `/cln/prod/*` (us-east-1) with `/cln/dr/*` (us-east-2) and prints a summary of missing parameters.

```bash
python check.py
```

---

### 🔹 Export Parameters with Values

Fetches all prod parameters with their values and exports them as a CSV — used as input for the remediation step.

```bash
python check1.py
```

---

### 🔹 Create Missing Parameters in DR

Reads the exported CSV and recreates all missing parameters in the DR region (`us-east-2`), preserving parameter types and KMS encryption.

```bash
python createdr.py
```

---

## 🔄 End-to-End Workflow

```
1. Deploy Lambda.py     →  Configure EventBridge rule to target it
2. SSM change in prod   →  Auto-replicated to DR in near real-time
3. Run check.py         →  Identify any configuration drift
4. Run check1.py        →  Export prod parameters with values to CSV
5. Run createdr.py      →  Bulk sync all missing parameters to DR
```

---

## 📊 Use Cases

- Disaster recovery readiness
- Multi-region configuration consistency
- Automated secret / config replication
- Failover reliability testing

---

## 🧠 Key Learnings

- Event-driven architecture using native AWS services
- Cross-region system design patterns
- Secure secret handling with KMS across regions
- Efficient configuration comparison and automated remediation


---

## 📋 Contributing

This project is open to contributions — if you have an idea to improve it, a bug to fix, or a feature to add, feel free to fork the repo, make your changes and open a pull request. All contributions are welcome, no matter how small.

If you use this on your profile, consider giving it a ⭐ — it helps others find it.

---

*Let's build together — fork it, break it, improve it.*

---
<div align="center">
  
**Built with ❤️ and lots of ☕ by Mayank Singh**

</div>
