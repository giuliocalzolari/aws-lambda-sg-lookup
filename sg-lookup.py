# -*- coding: utf-8 -*-
import boto3
import botocore
import json
import urllib2
import sys


def sendResponse(event, context, status, reason, data):
    # print status
    # print data
    # print context
    # print event
    PhysicalResourceId = data.get("GroupId","Error")

    responseBody = json.dumps({
        "Status": status,
        "Reason": reason,
        "PhysicalResourceId": PhysicalResourceId,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": data
    })

    print("RESPONSE BODY: %s" % (responseBody))

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(event["ResponseURL"], data=responseBody)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(responseBody))
    request.get_method = lambda: 'PUT'
    try:
        opener.open(request)
    except urllib2.HTTPError as e:
        print("urllib2.HTTPError: %s" % (e))
    except urllib2.URLError as e:
        print("urllib2.URLError: %s" % (e))
    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
    sys.exit(0)


def lambda_handler(event, context):

    reason = "CloudWatch Log Stream: " + context.log_stream_name
    if event['RequestType'] == "Delete":
        sendResponse(event, context, 'SUCCESS', reason, {})
    
    stack_region = event["StackId"].split(":")[3]
    status = 'FAILED'
    data = {}

    client = boto3.client('ec2', region_name=stack_region)
    try:
        response = client.describe_security_groups(
            Filters=[{'Name': 'vpc-id',   'Values': [event['ResourceProperties']['VpcId']] },
                     { 'Name': 'tag:Name', 'Values': [event['ResourceProperties']['SecurityGroupName']]}, 
            ])
        if response["SecurityGroups"] == []:
            reason = "SecurityGroup %s NOT FOUND" % (event['ResourceProperties']['SecurityGroupName'])
        else:
            data = response["SecurityGroups"][0]
            status = 'SUCCESS'
    except botocore.exceptions.ClientError as e:
        reason = e.message
    except IndexError as e:
        reason = "Error retriving SG info: %s " % e.message
    except:
        reason = e.message

    sendResponse(event, context, status, reason, data)

if __name__ == '__main__':
    class Struct:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    context_dict = {
        'aws_request_id': '2b8f996a-8622-11e6-980e-0bb09b880dcf',
        'log_stream_name': '2016/09/29/[$LATEST]f4a6e2d2b70747419538f07db1af1597',
        'invoked_function_arn': 'arn:aws:lambda:eu-west-1:123456789012:function:SecurityGroupLookup',
        'client_context': None,
        'log_group_name': '/aws/lambda/SecurityGroupLookup',
        'function_name': 'SecurityGroupLookup',
        'function_version': '$LATEST',
        'identity': "<__main__.CognitoIdentity object at 0x7f37b7ad99d0>",
        'memory_limit_in_mb': '128'
        }
    context = Struct(**context_dict)
    event = {'StackId': 'arn:aws:cloudformation:eu-west-1:123456789012:stack/cloudreach-wordpress-dev-toolbox/27657770-8622-11e6-99ca-500c423e34d2',
             'ResponseURL': 'https://cloudformation-custom-resource-response-eu-west1.s3-eu-west-1.amazonaws.com/arn%3Aaws%3Acloudformation%3Aeu-west-1%3A123456789012%3Astack/cloudreach-wordpress-dev-toolbox/27657770-8622-11e6-99ca-500c423e34d2%7CClusterGroup%7C372abc42-28d5-497d-b2e6-321c938f70d1?AWSAccessKeyId=AKIAJ7MCS7PVEUOADEEA&Expires=1475146399&Signature=UJHjS7%2BcwxtVXZymSCTTbnBqD2E%3D', 
             'ResourceProperties': {
                'ServiceToken': 'arn:aws:lambda:eu-west-1:123456789012:function:SecurityGroupLookup',
                'SecurityGroupName': 'demo-sg1',
                'VpcId': 'vpc-8ce407e9'
                },
            'RequestType': 'Create',
            'ServiceToken': 'arn:aws:lambda:eu-west-1:123456789012:function:SecurityGroupLookup',
            'ResourceType': 'Custom::SecurityGroupLookup',
            'RequestId': '372abc42-28d5-497d-b2e6-321c938f70d1',
            'LogicalResourceId': 'SGLookup'
            }
    lambda_handler(event,context)    