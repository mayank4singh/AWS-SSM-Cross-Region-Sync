import boto3
import csv

# Regions
PROD_REGION = "us-east-1"
DR_REGION = "us-east-2"

# Prefix mapping
SOURCE_PREFIX = "/cln/prod/"
TARGET_PREFIX = "/cln/dr/"

# Clients
ssm_prod = boto3.client("ssm", region_name=PROD_REGION)
ssm_dr = boto3.client("ssm", region_name=DR_REGION)


def get_all_params(client):
    params = []
    paginator = client.get_paginator("describe_parameters")

    for page in paginator.paginate():
        for p in page["Parameters"]:
            params.append(p["Name"])

    return params


print("Fetching PROD parameters...")
prod_params = get_all_params(ssm_prod)

print("Fetching DR parameters...")
dr_params = get_all_params(ssm_dr)

dr_set = set(dr_params)

drift = []

print("Comparing parameters...")

for param in prod_params:
    if param.startswith(SOURCE_PREFIX):
        expected_dr = param.replace(SOURCE_PREFIX, TARGET_PREFIX, 1)

        if expected_dr not in dr_set:
            drift.append([param, expected_dr, "Missing in DR"])


# Save CSV
with open("drift_report.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Prod Parameter", "Expected DR Parameter", "Status"])
    writer.writerows(drift)


print("\n✅ Drift report generated!")
print(f"Total PROD params: {len(prod_params)}")
print(f"Total DR params: {len(dr_params)}")
print(f"Missing in DR: {len(drift)}")