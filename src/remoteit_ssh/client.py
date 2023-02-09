import argparse
import json
import os
import requests
import sys

from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode


key_id = os.environ.get("R3_ACCESS_KEY_ID", None)
key_secret_id = os.environ.get("R3_SECRET_ACCESS_KEY", None)


def run_query(body):
    host = "api.remote.it"
    url_path = "/graphql/v1"
    content_type_header = "application/json"
    content_length_header = str(len(body))

    headers = {
        "host": host,
        "path": url_path,
        "content-type": content_type_header,
        "content-length": content_length_header,
    }

    response = requests.post(
        "https://" + host + url_path,
        json=body,
        auth=HTTPSignatureAuth(
            algorithm="hmac-sha256",
            key=b64decode(key_secret_id),
            key_id=key_id,
            headers=[
                "(request-target)",
                "host",
                "date",
                "content-type",
                "content-length",
            ],
        ),
        headers=headers,
    )

    if response.status_code == 403:
        print("Incorrect auth. Check your R3_* environment variables.")
        sys.exit(1)

    return response


def get_device_details_from_device_name(device_name):
    response = run_query(
        {
            "query": f"""
query {{
    login {{
        devices(name: "{device_name}") {{
            items {{
                id
                name
                services {{
                    id
                    name
                }}
            }}
        }}
    }}
}}"""
        }
    )

    return response.json()["data"]["login"]["devices"]["items"]


def get_ssh_details_from_device_name(device_name):
    device_details = get_device_details_from_device_name(device_name)

    if not device_details:
        print(f"Device matching {device_name} not found. Exiting.")
        sys.exit(1)

    remote_id = device_details[0]["services"][0]["id"]

    response = run_query(
        {
            "query": f"""
mutation {{
    connect(
        serviceId: "{remote_id}",
        hostIP: "0.0.0.0"
    ) {{
        host
        port
    }}
}}"""
        }
    )

    response = response.json()
    if "errors" in response:
        print("Error while trying to get device details:")

        if "inactive" in response["errors"][0]["message"]:
            print("\tDevice found but is inactive. Exiting.")
            sys.exit(1)
        else:
            print("\tUnknown error. Dumping entire error object:")
            print(response["errors"])
            sys.exit(1)

    return response["data"]["connect"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Matches a partial device name on Remoteit and opens an SSH connection to it."
    )

    parser.add_argument("device_name")

    return parser.parse_args()


def main():
    if not key_id or not key_secret_id:
        print(
            "You must set your env varialbes of R3_ACCESS_KEY_ID and R3_SECRET_ACCESS_KEY!"
        )
        sys.exit(1)

    args = parse_args()
    details = get_ssh_details_from_device_name(args.device_name)

    host = details["host"]
    port = details["port"]

    print(f"ssh -oStrictHostKeyChecking=no -p{port} pi@{host}")


if __name__ == "__main__":
    main()
