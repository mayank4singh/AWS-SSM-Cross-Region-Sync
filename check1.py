import boto3
import csv

ssm = boto3.client("ssm", region_name="us-east-1")

output_file = "prod_parameters_with_values.csv"

with open("drift_report.csv") as infile, open(output_file, "w", newline="") as outfile:
    reader = csv.DictReader(infile)
    
    fieldnames = ["Parameter Name", "Value", "Type"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        prod_param = row["Prod Parameter"]

        try:
            res = ssm.get_parameter(
                Name=prod_param,
                WithDecryption=True
            )

            param = res["Parameter"]

            writer.writerow({
                "Parameter Name": prod_param,
                "Value": param["Value"],
                "Type": param["Type"]
            })

            print(f"✅ Fetched: {prod_param}")

        except Exception as e:
            print(f"❌ Failed: {prod_param} → {e}")