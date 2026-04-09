import boto3
import json
import re

PRIMARY_REGION = "us-east-1"
DR_REGION = "us-east-2"

SOURCE_PREFIX = "/cln/prod/"
TARGET_PREFIX = "/cln/dr/"

ssm_primary = boto3.client("ssm", region_name=PRIMARY_REGION)
ssm_dr = boto3.client("ssm", region_name=DR_REGION)


def transform_value(value):
    
    value = re.sub(r"\bus-east-1\b", "us-east-2", value)
    value = re.sub(r"\buse1\b", "use2", value)
    value = re.sub(r"\.prod\.", ".dr.", value)
    value = re.sub(r"/prod/", "/dr/", value)

    return value


def lambda_handler(event, context):
    print("FULL EVENT:", json.dumps(event))

    try:
        detail = event.get("detail", {})
        operation = detail.get("operation")

        
        param_name = detail.get("name") or detail.get("requestParameters", {}).get("name")

        if not param_name:
            print("No parameter name found")
            return

        print(f"Operation: {operation}, Parameter: {param_name}")

       
        if not param_name.startswith(SOURCE_PREFIX):
            print("Skipping non-prod parameter")
            return

        
        target_name = param_name.replace(SOURCE_PREFIX, TARGET_PREFIX, 1)
        print(f"Target parameter: {target_name}")

        
        if operation == "Delete":
            try:
                ssm_dr.delete_parameter(Name=target_name)
                print(f"Deleted {target_name} from DR")
            except ssm_dr.exceptions.ParameterNotFound:
                print(f"{target_name} not found in DR")
            return

        
        if operation in ["Create", "Update"]:
            response = ssm_primary.get_parameter(
                Name=param_name,
                WithDecryption=True
            )

            param = response["Parameter"]
            original_value = param["Value"]

            
            transformed_value = transform_value(original_value)

            print(f"Original Value: {original_value}")
            print(f"Transformed Value: {transformed_value}")

            
            put_args = {
                "Name": target_name,
                "Value": transformed_value,
                "Type": param["Type"],
                "Overwrite": True
            }

            
            if param["Type"] == "SecureString":
                put_args["KeyId"] = "alias/aws/ssm"  

            ssm_dr.put_parameter(**put_args)

            print(f"Synced {param_name} → {target_name}")

    except Exception as e:
        print("Error occurred:", str(e))
        raise