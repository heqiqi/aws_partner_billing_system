import json
import boto3
import time
import csv
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
logger.info("test logging")


# update ACCOUNT_ID_LIST match your linked account id
ACCOUNT_ID_LIST = ["125391047781", "331059269292", "227976579875"]

def next_month():
    month = current_month()
    if month == 12:
        return 1
    else:
        return month + 1
    
def current_month():
    return datetime.utcnow().month

def current_year():
    return datetime.utcnow().year

def formatted_datetime():
    now = datetime.utcnow()
    formatted_now = now.strftime('%Y-%m-%d_%H:%M:%S')

    logger.info("running at: "+formatted_now)
    return formatted_now

def copy_obj(s3, source_bucket, source_key, target_bucket, target_key):
    logger.info("copy {} {} to {} {}".format(
        source_bucket, source_key, target_bucket, target_key))
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    s3.copy(copy_source, target_bucket, target_key)

def run_athena_query(query, database, bucket, s3_output):
    athena = boto3.client('athena')
    s3 = boto3.client('s3')
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': "s3://{}/{}".format(bucket, s3_output),
        }
    )
    
    logger.info(f'Started query: {response["QueryExecutionId"]}')
    execution_id = response["QueryExecutionId"]
    while True:
        response = athena.get_query_execution(QueryExecutionId=execution_id)

        if response['QueryExecution']['Status']['State'] in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break

        logger.info("Waiting for query to finish...")
        time.sleep(5)

    if response['QueryExecution']['Status']['State'] == 'SUCCEEDED':
        logger.info("Query succeeded, loading results to DynamoDB")

        # Load results from S3 and write to DynamoDB
        result_file = s3_output + execution_id + '.csv'
        logger.info("result file: {}".format(result_file))
        s3.download_file(bucket, result_file, '/tmp/results.csv')
        copy_obj(s3, bucket, result_file, bucket, s3_output+ formatted_datetime() +"/"+execution_id + '.csv')

    elif response['QueryExecution']['Status']['State'] == 'FAILED':
        logger.info(f"Query failed, reason: {response['QueryExecution']['Status']['StateChangeReason']}")

    elif response['QueryExecution']['Status']['State'] == 'CANCELLED':
        logger.info("Query was cancelled")

def query_item(table_name, partition_name, partition_value):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression='#partitionKeyName = :partitionkeyval',
        ExpressionAttributeNames={
        '#partitionKeyName': partition_name,
        },
        ExpressionAttributeValues={
            ':partitionkeyval': partition_value,
        }
    )
    logger.info(str(response))
    items = response['Items']
    return items

def delete_item(table_name, partition_key, sort_key=None):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    items = query_item(table_name, 'account_month', partition_key)
    for i in items:
        key = {
            'account_month': partition_key,
            'product_usage_type_quantity': i['product_usage_type_quantity']
        }
        if sort_key is not None:
            key['product_usage_type_quantity'] = sort_key
    
        response = table.delete_item(Key=key)
    

def parse_csv_to_ddb(account_id, month, table_name):
    dynamodb = boto3.resource('dynamodb')
    dynamodb_table = dynamodb.Table(table_name)
    logger.info("delete {}".format(str(account_id)+"_"+str(month)))
    delete_item(table_name, str(account_id)+"_"+str(month))
    logger.info("delete  complete")

    with open('/tmp/results.csv', 'r') as data:
            next(data)  # Skip the header row
            reader = csv.reader(data)
            for row in reader:
                # logger.info("row: {}".format(row))
                item = {
                    'account_month': str(account_id)+"_"+str(month),
                    'product_usage_type_quantity': row[0]+row[1]+row[3],
                    'product_product_name': row[0],
                    'line_item_usage_type': row[1],
                    'line_item_line_item_description': row[2],
                    'bill_payer_account_id': row[3],
                    'usage_quantity': row[4],
                    'pricing_unit': row[5],
                    'cost': row[6],
                    'createAt': int(datetime.now().timestamp()*1000)
                }
                if item['cost'] == '0.0':
                    logger.info("cost 0.0, next")
                    continue
                dynamodb_table.put_item(Item=item)

def get_invoke_account_id(context):
    return context.invoked_function_arn.split(":")[4]

def lambda_handler(event, context):
    logger.info("lambda_handler event: {}".format(event))
    executor = get_invoke_account_id(context)
    for ACCOUNT_ID in ACCOUNT_ID_LIST:
        database = "monthly-cur-{}".format(ACCOUNT_ID)
        ddb_database = "monthly-cur-{}".format("whole-org")
        query = '''SELECT "product_product_name", "line_item_usage_type", "line_item_line_item_description", "bill_payer_account_id", round(sum("line_item_usage_amount"),3) as "usage_quantity", "pricing_unit", round(sum("line_item_unblended_cost"),2) as cost from "{}"."organization_enable_cur"
 WHERE "bill_billing_period_start_date" >= cast('{}-{}-01' as DATE) and "bill_billing_period_end_date" <= cast('{}-{}-01' as DATE)   
 GROUP BY "line_item_product_code","bill_payer_account_id", "product_product_name", "line_item_usage_type","pricing_unit", "line_item_line_item_description"
 ORDER BY cost desc
 LIMIT 100'''.format(database,current_year(), current_month(), current_year(), next_month())
        bucket = "org-cur-integration-{}".format(executor)
        s3_output = "query-results/{}/".format(ACCOUNT_ID)
        run_athena_query(query, database, bucket, s3_output)
        parse_csv_to_ddb(ACCOUNT_ID, current_month(), ddb_database)

    return {
        'statusCode': 200,
        'body': json.dumps('Complete')
    }
