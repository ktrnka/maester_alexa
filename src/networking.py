from __future__ import unicode_literals
from __future__ import print_function

import elasticsearch
import private
from aws_requests_auth.aws_auth import AWSRequestsAuth


def get_aws_auth():
    """Get HTTP authentication for our Elastic Search AWS user"""
    return AWSRequestsAuth(aws_access_key=private.ES_ACCESS_KEY_ID,
                           aws_secret_access_key=private.ES_SECRET_ACCESS_KEY,
                           aws_host=private.ES_HOST,
                           aws_region=private.ES_REGION,
                           aws_service="es")

def get_elasticsearch():
    """Get an Elastic Search handle with AWS authentication"""
    return elasticsearch.Elasticsearch(hosts=private.ES_URL,
                                       connection_class=elasticsearch.RequestsHttpConnection,
                                       http_auth=get_aws_auth())