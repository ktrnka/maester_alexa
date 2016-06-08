from __future__ import unicode_literals
from __future__ import print_function
import sys
import argparse

import private
from aws_requests_auth.aws_auth import AWSRequestsAuth


def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == "__main__":
    sys.exit(main())


def get_aws_auth():
    return AWSRequestsAuth(aws_access_key=private.ES_ACCESS_KEY_ID,
                           aws_secret_access_key=private.ES_SECRET_ACCESS_KEY,
                           aws_host=private.ES_HOST,
                           aws_region=private.ES_REGION,
                           aws_service="es")