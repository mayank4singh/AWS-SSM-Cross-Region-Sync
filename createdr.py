import boto3
import csv
import time

session = boto3.Session()  

ssm_dr = session.client("ssm", region_name="us-east-2")

def convert_to_dr_name(name):
    return name.replace("/cln/prod/", "/cln/dr/", 1)

def create_parameter(row):
    prod_name = row["Parameter Name"]
    dr_name = convert_to_dr_name(prod_name)

    value = row["Value"]
    param_type = row["Type"]

    try:
        # Optional: Skip if already exists
        try:
            ssm_dr.get_parameter(Name=dr_name)
            print(f"⚠️ Already exists: {dr_name}")
            return
        except:
            pass

        kwargs = {
            "Name": dr_name,
            "Value": value,
            "Type": param_type,
            "Overwrite": True
        }

        # Handle SecureString
        if param_type == "SecureString":
            kwargs["KeyId"] = "alias/aws/ssm"

        ssm_dr.put_parameter(**kwargs)

        print(f"✅ Created: {dr_name}")

        # Avoid throttling
        time.sleep(0.05)

    except Exception as e:
        print(f"❌ Failed: {dr_name} → {e}")


# 👉 Input CSV (your generated file)
csv_file = "prod_parameters_with_values.csv"

with open(csv_file, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        create_parameter(row)