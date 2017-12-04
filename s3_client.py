#!/usr/bin/env python3
"""
Small Amazon AWS S3 management client
"""
import sys
import requests
import requests_aws4auth as aws4auth
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import mimetypes

access_id = ""
access_key = "d"
region = "us-west-2"
endpoint = "s3-{}.amazonaws.com".format(region)
auth = aws4auth.AWS4Auth(access_id, access_key, region, "s3")
ns = "http://s3.amazonaws.com/doc/2006-03-01/"


def xml_pretty_print(xml_string):
    print(minidom.parseString(xml_string).toprettyxml())


def create_bucket(bucket):
    XML = ET.Element("CreateBucketConfiguration")
    XML.attrib["xmlns"] = ns

    location = ET.SubElement(XML, "LocationConstraint")
    location.text = auth.region

    data = ET.tostring(XML, encoding="utf-8")
    url = "http://{}.{}".format(bucket, endpoint)
    r = requests.put(url, data=data, auth=auth)
    if r.ok:
        print("Created bucket {} OK".format(bucket))
    else:
        handle_errors(r)


def upload_file(bucket, s3_name, local_path, acl="private"):
    data = open(local_path, "rb").read()
    url = "http://{}.{}/{}".format(bucket, endpoint, s3_name)
    headers = {"x-amz-acl": acl}

    mimetype = mimetypes.guess_type(local_path)[0]
    if mimetype:
        headers["Content-Type"] = mimetype

    r = requests.put(url, data=data, headers=headers, auth=auth)
    if r.ok:
        print("Uploaded {} OK".format(local_path))
    else:
        handle_errors(r)


def download_file(bucket, s3_name, local_path):
    url = "http://{}.{}/{}".format(bucket, endpoint, s3_name)
    r = requests.get(url, auth=auth)
    if r.ok:
        open(local_path, "wb").write(r.content)
        print("Downloaded {} OK".format(s3_name))
    else:
        handle_errors(r)


def handle_errors(response):
    output = "Status code: {}\n".format(response.status_code)
    root = ET.fromstring(response.text)
    code = root.find("Code").text
    output += "Error code: {}\n".format(code)
    message = root.find("Message").text
    output += "Message: {}\n".format(message)
    print(output)


if __name__ == '__main__':
    cmd, *args = sys.argv[1:]
    globals()[cmd](*args)
