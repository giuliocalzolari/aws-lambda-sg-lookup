# AWS Lambda Security Group Lookup

## Overview ##
This AWS Lambda function allowed to retrieve SecurityGroupId from Cloudformation using Custom Resource


## How To install ##


```
$ aws iam create-role --role-name sg-lookup-role \
	--assume-role-policy-document file://iam_policy/trust_policy.json

```

```
$ aws iam put-role-policy --role-name sg-lookup-role \
    --policy-name sg_lookup_policy \
    --policy-document file://iam_policy/sg_lookup_policy.json
```

```
$ zip sg-lookup.zip sg-lookup.py
```

```
$ aws lambda create-function \
	--region eu-west-1 \
	--function-name SecurityGroupLookup \
	--zip-file fileb://sg-lookup.zip \
	--description "SecurityGroupLookup" \
	--role arn:aws:iam::123456789012:role/sg-lookup-role \
	--handler sg-lookup.lambda_handler \
	--runtime python2.7 \
	--timeout 180
```



## Cloudformation Example with SecurityLookup Integration

```
{
    "Description": "Ec2 Ubuntu 14.04 with SecurityLookup Integration",
    "Mappings": {
        "AWSRegion2AMI": {
            "ap-northeast-1": {"AMI": "ami-936d9d93"},
            "ap-southeast-1": {"AMI": "ami-96f1c1c4"},
            "ap-southeast-2": {"AMI": "ami-69631053"},
            "eu-central-1": {"AMI": "ami-accff2b1"},
            "eu-west-1": {"AMI": "ami-47a23a30"},
            "sa-east-1": {"AMI": "ami-4d883350"},
            "us-east-1": {"AMI": "ami-d05e75b8"},
            "us-west-1": {"AMI": "ami-df6a8b9b"},
            "us-west-2": {"AMI": "ami-5189a661"}
        }},
    "Parameters": {
        "InstanceType": {
            "AllowedValues": [
                "t2.micro",
                "t2.medium",
                "m3.medium",
                "m3.large",
                "m3.xlarge",
                "m3.2xlarge"
            ],
            "ConstraintDescription": "must be a valid EC2 instance type.",
            "Default": "t2.micro",
            "Description": "Instance type",
            "Type": "String"
        },
        "KeyName": {
            "ConstraintDescription": "must be the name of an existing EC2 KeyPair.",
            "Description": "Name of an existing EC2 KeyPair to enable SSH access to the instances",
            "Type": "AWS::EC2::KeyPair::KeyName"
        },
        "Subnet1": {
            "Description": "Subnet1 ID",
            "Type": "AWS::EC2::Subnet::Id"
        },
        "VpcId": {
            "Description": "VpcId",
            "Type": "AWS::EC2::VPC::Id"
        }
    },
    "Resources": {
        "Ec2SGLookup": {
            "Type": "Custom::SecurityGroupLookup"
            "Properties": {
                "SecurityGroupName": "jump-sg",
                "ServiceToken": {
                    "Fn::Join": ["",[ "arn:aws:lambda:eu-west-1:", { "Ref": "AWS::AccountId" }, ":function:SecurityGroupLookup" ]]
                },
                "VpcId": { "Ref": "VpcId" }
            }
        },
        "JumpBox": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "ImageId": { "Fn::FindInMap": [ "AWSRegion2AMI", { "Ref": "AWS::Region" }, "AMI" ] },
                "InstanceType": { "Ref": "InstanceType" },
                "KeyName": { "Ref": "KeyName" },
                "SecurityGroupIds": [ { "Fn::GetAtt": [ "Ec2SGLookup", "GroupId" ] } ],
                "SubnetId": { "Ref": "Subnet1" },
                "Tags": [ { "Key": "Name", "Value": "JumpBox" } ],
                "UserData": {
                    "Fn::Base64": { "Fn::Join": [ "",["#!/bin/bash -v\n","apt-get update\n" ] ]}
                }
            }
        }
    }
}
```

## Thanks

Keep It Cloudy ([@CloudreachKIC](https://twitter.com/cloudreachkic))

## Contributing

1. Create your fork by clicking Fork button on top of the page.
2. Download your repository: `git clone https://github.com/USER/aws-lambda-sg-lookup.git`
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'My new feature description'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## License
The MIT License (MIT)
Copyright (c) 2016 Giulio Calzolari

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
