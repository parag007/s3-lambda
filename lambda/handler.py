import json
import logging
import os
import urllib.parse

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def lambda_handler(event, context):
    
    #Itarate through multiple records
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        
        # S3 event notifications URL-encode
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        logger.info("Processing s3://%s/%s", bucket, key)

        #Fetch and decode as UTF-8
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
        line = body.strip()
        parsed = parse_line(line)

        logger.info("Parsed key=%s format=%s data=%s", key, parsed["format"], parsed["data"])

    return {"statusCode": 200}


def parse_line(line: str) -> dict:
    #Parse a single line: try JSON else plain text.
    if not line:
        return {"format": "empty", "data": None}
    
    try:
        return {"format": "json", "data": json.loads(line)}
    except json.JSONDecodeError:
        return {"format": "text", "data": line}
