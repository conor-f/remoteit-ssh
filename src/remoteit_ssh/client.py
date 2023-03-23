import argparse
import configparser
import json
import os
import requests
import sys

from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode


def run_query(body, key_id, key_secret_id):
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
        print("Incorrect auth")
        sys.exit(1)

    return response


def get_device_details_from_device_name(device_name, key_id, key_secret_id):
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
        },
        key_id,
        key_secret_id,
    )

    return response.json()["data"]["login"]["devices"]["items"]


def get_ssh_details_from_device_name(device_name, key_id, key_secret_id):
    device_details = get_device_details_from_device_name(
        device_name, key_id, key_secret_id
    )

    if not device_details:
        print(f"Device matching {device_name} not found")
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
        },
        key_id,
        key_secret_id,
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

    parser.add_argument(
        "-f",
        "--file",
        default="~/.config/remoteit_ssh/config.ini",
        help="Filepath for a config file to use",
    )

    parser.add_argument(
        "-p",
        "--profile",
        default="default",
        help="Which profile to use. Must match a section in your config file.",
    )

    parser.add_argument("device_name")

    return parser.parse_args()


def get_from_config_file(filepath, profile, option):
    config = configparser.ConfigParser()

    # Needed to account for ~/ in filepath.
    config.read(os.path.expanduser(filepath))

    if not config:
        print(f"Cannot parse config file at {filepath}")
        sys.exit(1)

    if profile not in config.sections():
        print(f"Profile {profile} not found in config file {filepath}")
        sys.exit(1)

    return config.get(profile, option, fallback=None)


def get_key_id(args):
    key_id = get_from_config_file(args.file, args.profile, "R3_ACCESS_KEY_ID")

    if not key_id:
        print("Couldn't parse key_id.")
        sys.exit(1)

    return key_id


def get_key_secret_id(args):
    key_secret_id = get_from_config_file(
        args.file, args.profile, "R3_SECRET_ACCESS_KEY"
    )

    if not key_secret_id:
        print("Couldn't parse key_secret_id.")
        sys.exit(1)

    return key_secret_id


def main():
    args = parse_args()

    key_id = get_key_id(args)
    key_secret_id = get_key_secret_id(args)
    device_name = args.device_name

    details = get_ssh_details_from_device_name(
        device_name,
        key_id,
        key_secret_id,
    )

    host = details["host"]
    port = details["port"]

    print(f"ssh -oStrictHostKeyChecking=no -p{port} pi@{host}")


if __name__ == "__main__":
    main()
