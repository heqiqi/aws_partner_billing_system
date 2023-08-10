import json
import boto3
import os
import uuid

from datetime import datetime

# CONST VARIABLE
LINKED_CUR_PREFIX = 'organization-enable-cur-'
##OBJECT_KEY = 'cost-monthly-parquet/cost-monthly-parquet/cost-monthly-parquet/year=2023/month=6/cost-monthly-parquet-00001.snappy.parquet'
OBJECT_KEY = 'monthly-cur-'
TARGET_BUKET = 'org-cur-integration-'
region = os.environ['AWS_REGION']
#cur_bucket = os.environ['ORG_CUR_BUCKET']


def generate_obj_prefix():
    return 'monthly/year='+datetime.now().year+'/month='+datetime.now().month+'/cost-monthly-parquet-00001.snappy.parquet'


def get_invoke_account_id(context):
    return context.invoked_function_arn.split(":")[4]


def get_linked_account_list():
    accList = get_active_accounts()
    return [acc['Id'] for acc in accList]


def get_active_accounts():
    client = boto3.client('organizations')
    paginator = client.get_paginator('list_accounts')

    active_accounts = []
    for page in paginator.paginate():
        for account in page['Accounts']:
            if account['Status'] == 'ACTIVE':
                active_accounts.append(account)

    return active_accounts


def copy_obj(s3, source_bucket, source_key, target_bucket, target_key):
    print("copy {} {} to {} {}".format(
        source_bucket, source_key, target_bucket, target_key))
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    s3.copy(copy_source, target_bucket, target_key)


def copy_all_objects_in_folder(source_bucket, source_prefix, target_bucket, target_prefix):
    s3 = boto3.resource('s3')

    source_bucket_obj = s3.Bucket(source_bucket)
    target_bucket_obj = s3.Bucket(target_bucket)

    for src_obj in source_bucket_obj.objects.filter(Prefix=source_prefix):
        print("copy....: " + src_obj.key)
        source = {
            'Bucket': source_bucket,
            'Key': src_obj.key
        }
        new_key = src_obj.key.replace(source_prefix, target_prefix, 1)
        target_bucket_obj.copy(source, new_key)


def prefix_exits(s3, bucket, prefix):
    res = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    return 'Contents' in res

def list_crawlers(crawer_name):
    glue = boto3.client('glue')
    response = glue.get_crawler(Name=crawer_name)
    # crawlers = response['Crawlers']
    print("list_crawler: "+str(response))


def lambda_handler(event, context):
    aws_account_id = get_invoke_account_id(context)
    print('account id:{} bucket: {}'.format(aws_account_id, TARGET_BUKET+aws_account_id))
     # Create an S3 client
    s3 = boto3.client('s3')
    accout_list = get_linked_account_list()
    for acc in accout_list:
        print('account: {}'.format(acc))
        try:
            isExist = prefix_exits(s3, LINKED_CUR_PREFIX+acc, OBJECT_KEY+acc)
            print(isExist)
            if isExist:
                print('copying..')
                copy_all_objects_in_folder(LINKED_CUR_PREFIX+acc, OBJECT_KEY+acc, TARGET_BUKET+aws_account_id, acc+'/monthly')
                print("copy done")
                list_crawlers("cur_crawler_{}".format(acc))
            else:
                print("not existed")
        except Exception as e:
                print(e)
        break

    result = {"msg": "ok"}
    return str(result)

