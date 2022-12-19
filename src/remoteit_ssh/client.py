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

    return response


def get_active_device_from_device_name(device_name):
    response = run_query(
        {
            "query": f"""
query {{
    login {{
        devices(state: "active", name: "{device_name}") {{
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
    device_details = get_active_device_from_device_name(device_name)

    remote_id = device_details[0]
    remote_id = remote_id["services"][0]["id"]

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

    return response.json()["data"]["connect"]


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

    print(f"ssh -p{port} pi@{host}")


if __name__ == "__main__":
    main()
