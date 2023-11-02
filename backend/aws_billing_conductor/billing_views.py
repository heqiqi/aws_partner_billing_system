import csv
from datetime import datetime

import boto3
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet, ModelViewSet

from dvadmin.utils.json_response import DetailResponse, ErrorResponse

from .aws_service import AwsCliService
from dvadmin.system.models import Dept

import logging

from .billing_conductor_payload import delete_group_body, create_group_body, create_price_rule, \
    create_pricing_rule_body, create_pricing_plan_body, update_bill_group

logger = logging.getLogger(__name__)


@api_view(['PUT'])
def sample_put_view(request):
    data = {
        'message': 'PUT request successful'
    }
    return DetailResponse(data=data)


def getAccountIdFromRequest(request):
    param = request.GET.copy()
    accId = param.get('account_id', None)
    logger.info("account_id: {}".format(accId))
    return accId


class AwsBillingConductorGroupModelViewSet(ViewSet):

    # queryset = AwsBillingConductorGroupModel.objects.all()
    # serializer_class = AwsBillingConductorGroupModelSerializer
    # create_serializer_class = AwsBillingConductorGroupModelCreateUpdateSerializer
    # update_serializer_class = AwsBillingConductorGroupModelCreateUpdateSerializer
    # filter_fields = ['name', 'size']
    # search_fields = ['name']

    def genPayload(self, request):
        now = datetime.now()
        date_string = now.strftime("%Y-%m")
        return {
            "BillingPeriod": date_string,
            "Filters": {},
            "MaxResults": 96
        }

    def getAwsClient(self, request):
        ak = request.user.dept.access_key if request.user.dept is not None else None
        sk = request.user.dept.secret_key if request.user.dept is not None else None
        accId = getAccountIdFromRequest(request)
        if accId is not None:
            dept = Dept.objects.filter(account_id=accId)
            ak = dept[0].access_key
            sk = dept[0].secret_key
        return AwsCliService(ak, sk)

    def get_dynamodb_client(self, request):
        ak = request.user.dept.access_key if request.user.dept is not None else None
        sk = request.user.dept.secret_key if request.user.dept is not None else None
        accId = getAccountIdFromRequest(request)
        if accId is not None:
            dept = Dept.objects.filter(account_id=accId)
            ak = dept[0].access_key
            sk = dept[0].secret_key
        return boto3.resource('dynamodb',
                                   aws_access_key_id=ak,
                                   aws_secret_access_key=sk,
                                   region_name='us-east-1')

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def list_pricing_plans(self, request):
        """
        获取pricing_plans列表
        """

        logger.info('list_pricing_plans')
        aws_client = self.getAwsClient(request)
        load = self.genPayload(request)
        billing_group = aws_client.list_pricing_plans(load)
        return DetailResponse(data=billing_group)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def list_pricing_rules(self, request):
        aws_client = self.getAwsClient(request)
        param = request.GET.copy()
        logger.info('list_account_associations{}'.format(param.get('arn')))
        arn = param.get('arn')

        load = self.genPayload(request)
        if arn is not None:
            load['Filters']['Arn'] = [arn]
        pricing_rules = aws_client.list_pricing_rules(load)
        return DetailResponse(data=pricing_rules)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def list_billing_group_cost_reports(self, request):
        aws_client = self.getAwsClient(request)
        billing_group = aws_client.list_billing_group_cost_reports(self.genPayload(request))
        return DetailResponse(data=billing_group)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def bill_group_remote(self, request):
        now = datetime.now()
        date_string = now.strftime("%Y-%m")
        aws_client = self.getAwsClient(request)
        bill = {
            "BillingPeriod": date_string,
            "Filters": {},
            "MaxResults": 96
        }
        billing_group = aws_client.get_bill_group_list(bill)
        return DetailResponse(data=billing_group)

    @swagger_auto_schema(method='post', request_body=delete_group_body, )
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def delete_billing_group(self, request):
        request_data = request.data
        arn = request_data.get('arn', None)
        logger.debug("{}".format(request))
        aws_client = self.getAwsClient(request)
        data = {
            "Arn": arn
        }
        ret = aws_client.delete_billing_group(data)
        return DetailResponse(data=ret)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def list_account_associations(self, request):
        aws_client = self.getAwsClient(request)
        param = request.GET.copy()
        logger.info('list_account_associations{}'.format(param.get('arn')))
        arn = param.get('arn')
        Association = 'UNMONITORED' if arn is None else arn
        date_string = datetime.now().strftime("%Y-%m")
        data = {
            "BillingPeriod": date_string,
            "Filters": {'Association': Association}
        }
        account_list = aws_client.list_account_associations(data)
        return DetailResponse(data=account_list)

    @swagger_auto_schema(method='post', request_body=create_group_body, )
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_billing_group(self, request):
        request_data = request.data
        logger.info("create_billing_group:\n\n{}".format(request.data))
        aws_client = self.getAwsClient(request)
        pricePlanArn = ''
        if request_data['isCreatePlan']:
            discount = 100 - int(request_data['discount'])
            dType = 'DISCOUNT' if discount >= 0 else 'MARKUP'
            if discount < 0:
                discount = -discount
            priceRule = {
                "Type": dType,
                "ModifierPercentage": float(discount),
                "Name": "{}_{}_{}_pRule{}".format(request_data['name'], dType, discount,
                                                  int(datetime.timestamp(datetime.now()))),
                "Scope": 'GLOBAL'
            }

            pPlan = aws_client.create_pricing_rule(priceRule)
            pricePlan = {
                "PricingRuleArns": [pPlan['Arn']],
                "Description": "{}_{}_{}_pricePlan_{}".format(request_data['name'], dType, discount,
                                                              datetime.now().strftime("%m-%d:%H:%M:%S")),
                "Name": "{}_{}_{}_{}".format(request_data['name'], dType, discount,
                                             int(datetime.timestamp(datetime.now())))
            }
            pPlan = aws_client.create_pricing_plan(pricePlan)
            logger.info("pPlan:\n\n{}".format(pPlan['Arn']))
            pricePlanArn = pPlan['Arn']
        else:
            pricePlanArn = request_data['checkedpricePlan']
        bg = {
            "Name": request_data['name'],
            "Description": request_data['description'],
            "ComputationPreference": {"PricingPlanArn": pricePlanArn},
            "AccountGrouping": {"LinkedAccountIds": request_data['checkedAccount']},
            "PrimaryAccountId": request_data['checkedPrimaryAccount']
        }

        ret = aws_client.create_billing_group(bg)
        return DetailResponse(data=ret['Arn'])

    @swagger_auto_schema(method='post', request_body=create_price_rule, )
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_pricing_plan_rule(self, request):
        request_data = request.data
        logger.info("create_pricing_plan_rule:\n\n{}".format(request.data))
        logger.info("create_pricing_plan_rule accoundId:\n\n{}".format(accId))
        aws_client = self.getAwsClient(request)
        discount = 100 - int(request_data['discount'])
        dType = 'DISCOUNT' if discount >= 0 else 'MARKUP'
        if discount < 0:
            discount = -discount
        PriceRuleName = "{}_{}_{}_Rule{}".format(request_data['name'], dType, discount,
                                                 int(datetime.timestamp(datetime.now())))
        priceRule = {
            "Type": dType,
            "ModifierPercentage": float(discount),
            "Name": PriceRuleName,
            "Scope": 'GLOBAL'
        }

        pPlan = aws_client.create_pricing_rule(priceRule)
        PricePlanName = "{}_{}_{}_{}".format(request_data['name'], dType, discount,
                                             int(datetime.timestamp(datetime.now())))
        pricePlan = {
            "PricingRuleArns": [pPlan['Arn']],
            "Description": "{}_{}_{}_pricePlan_{}".format(request_data['name'], dType, discount,
                                                          datetime.now().strftime("%m-%d:%H:%M:%S")),
            "Name": PricePlanName
        }
        pPlan = aws_client.create_pricing_plan(pricePlan)
        logger.info("pPlan:\n\n{}".format(pPlan['Arn']))
        return DetailResponse(data={"Arn": pPlan['Arn'], "Name": PricePlanName})

    @swagger_auto_schema(method='post', request_body=create_pricing_rule_body)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_pricing_rule(self, request):
        # arn = request_data.get('arn', None)
        logger.debug("{}".format(request))
        aws_client = self.getAwsClient(request)
        ret = aws_client.create_pricing_rule(request.data)
        return DetailResponse(data=ret)

    @swagger_auto_schema(method='post', request_body=create_pricing_plan_body, )
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_pricing_plan(self, request):
        # arn = request_data.get('arn', None)
        logger.debug("{}".format(request))
        aws_client = self.getAwsClient(request)
        ret = aws_client.create_pricing_plan(request.data)
        return DetailResponse(data=ret)

    @swagger_auto_schema(method='post', request_body=update_bill_group)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def update_billing_group(self, request):
        logger.info("update_billing_group:\n\n\n{}".format(request.data))
        aws_client = self.getAwsClient(request)
        primaryAcc = request.data['PrimaryAccountId']
        arn = request.data['Arn']
        OldAccounts = [d['AccountId'] for d in request.data['OldAccounts'] if d['AccountId'] != primaryAcc]
        if len(OldAccounts) > 0:
            logger.info("disassociateAccs:\n\n\n{}".format(OldAccounts))
            result = self.associate_accounts(request, False, arn, OldAccounts)
            logger.info("disassociate_accounts: {}".format(result))

        NewAccounts = [d['AccountId'] for d in request.data['Accounts'] if d['AccountId'] != primaryAcc]
        if len(NewAccounts) > 0:
            logger.info("associateAccs:\n\n\n{}".format(NewAccounts))
            result = self.associate_accounts(request, True, arn, NewAccounts)
            logger.info("associate_accounts: {}".format(result))

        updateBillGroup = {
            "Arn": request.data['Arn'],
            "ComputationPreference": request.data['ComputationPreference']
        }
        ret = aws_client.update_billing_group(updateBillGroup)
        logger.info("update_billing_group: {}".format(ret))
        return DetailResponse(data=ret)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def list_custom_line_items(self, request):
        aws_client = self.getAwsClient(request)
        custom_line = aws_client.list_custom_line_items(self.genPayload(request))
        return DetailResponse(data=custom_line)

    @swagger_auto_schema(method='post',
                         request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['Arn'], properties={
                             'Arn': openapi.Schema(type=openapi.TYPE_STRING,
                                                   description='AWS Arn')}))
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def delete_custom_line_items(self, request):
        logger.info("{}".format(request.data))
        aws_client = self.getAwsClient(request)
        isPercent = request.data['ChargeDetails'].get('Flat') is None
        logger.info("isPercent: {}".format(request.data['ChargeDetails'].get('Flat')))
        if isPercent:
            self.batch_disassociate_resources_from_custom_line_item(request)
        customLineDelete = {
            "Arn": request.data['Arn'],
            "BillingPeriodRange": {"InclusiveStartBillingPeriod": datetime.now().strftime("%Y-%m")}
        }
        ret = aws_client.delete_custom_line_items(customLineDelete)
        return DetailResponse(data=ret)

    @swagger_auto_schema(method='post',
                         request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                     required=['Name', 'Description', 'BillingGroupArn'], properties={
                                 'Name': openapi.Schema(type=openapi.TYPE_STRING,
                                                        description='customer line item Name'),
                                 'Description': openapi.Schema(type=openapi.TYPE_STRING, description='AWS Description'),
                                 'BillingGroupArn': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   description=' BillingGroupArn')}))
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_custom_line_item(self, request):
        logger.info("create_custom_line_item： {}".format(request.data))
        aws_client = self.getAwsClient(request)
        amount = 0
        parseCharges = {'Type': 'CREDIT'}
        if request.data['Fee'] == '' and request.data['Credit'] != '':
            parseCharges['Type'] = 'CREDIT'
            amount = round(float(request.data['Credit']), 0)
        elif request.data['Fee'] != '' and request.data['Credit'] == '':
            parseCharges['Type'] = 'FEE'
            amount = round(float(request.data['Fee']), 0)

        if request.data['isFlat'] == 'true':
            parseCharges['Flat'] = {'ChargeValue': amount}
        else:
            parseCharges['Percentage'] = {'PercentageValue': amount,
                                          'AssociatedValues': [request.data['BillingGroupArn']]}

        customLineDelete = {
            "Name": request.data['Name'],
            "Description": request.data['Description'],
            "BillingGroupArn": request.data['BillingGroupArn'],
            "BillingPeriodRange": {"InclusiveStartBillingPeriod": datetime.now().strftime("%Y-%m")},
            "ChargeDetails": parseCharges
        }
        ret = aws_client.create_custom_line_item(customLineDelete)
        return DetailResponse(data=ret)

    def batch_disassociate_resources_from_custom_line_item(self, request):
        aws_client = self.getAwsClient(request)
        unassociate = {
            "TargetArn": request.data['Arn'],
            "ResourceArns": [
                request.data['BillingGroupArn'],
            ],
            # "BillingPeriodRange": {"InclusiveStartBillingPeriod": "2023-06","ExclusiveEndBillingPeriod": "2023-07"}
            "BillingPeriodRange": {"InclusiveStartBillingPeriod": datetime.now().strftime("%Y-%m")}
        }
        ret = aws_client.batch_disassociate_resources_from_custom_line_item(unassociate)
        return ret


    def associate_accounts(self, request, isAssociate, arn, accountIds):
        aws_client = self.getAwsClient(request)
        data = {
            'Arn': arn,
            'AccountIds': accountIds
        }
        if isAssociate:
            return aws_client.associate_accounts(data)
        else:
            return aws_client.disassociate_accounts(data)

    @swagger_auto_schema(method='post',
                         request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['Arn'], properties={
                             'Arn': openapi.Schema(type=openapi.TYPE_STRING,description='AWS Pricing Rule Arn')}))
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def pricing_rule_details_by_pricing_plan(self, request):
        aws_client = self.getAwsClient(request)
        now = datetime.now()
        date_string = now.strftime("%Y-%m")
        data = {
            'BillingPeriod': date_string,
            'PricingPlanArn': request.data['Arn']
        }
        pRule = aws_client.list_pricing_rules_associated_to_pricing_plan(data)
        logger.info("list_pricing_rules_associated_to_pricing_plan: {}".format(pRule))
        if pRule['PricingRuleArns'] is not None and len(pRule['PricingRuleArns']) > 0:
            pRuleList = pRule['PricingRuleArns']
            data = self.genPayload(request)
            data['Filters'] = {'Arns': pRuleList}
            ret = aws_client.list_pricing_rules(data)
            logger.info("list_pricing_rules: {}".format(ret))
            return DetailResponse(data=ret)
        else:
            return ErrorResponse(msg='No pricing rule found')

    def get_billings(self, dynamodb, b_account_id, is_current_month):
        table = dynamodb.Table('monthly-cur-whole-org')
        today = datetime.today()
        monthStr = str(datetime.now().month)
        if is_current_month == '0':
            monthStr = str((today.month - 1) if (today.month > 1) else 12)
        return table.query(
            KeyConditionExpression='#partitionKeyName = :partitionkeyval',
            ExpressionAttributeNames={
                '#partitionKeyName': 'account_month',
            },
            ExpressionAttributeValues={
                ':partitionkeyval': b_account_id + "_" + monthStr,
            }
        )
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def account_monthly_bill(self, request):
        b_account_id = request.GET.copy().get('bill_account_id', None)
        is_current_month = request.GET.copy().get('is_current_month', None)
        dynamodb = self.get_dynamodb_client(request)
        response = self.get_billings(dynamodb, b_account_id, is_current_month)
        items = response['Items']
        return DetailResponse(data=items)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def download_monthly_bill(self, request):
        b_account_id = request.GET.copy().get('bill_account_id', None)
        is_current_month = request.GET.copy().get('is_current_month', None)
        dynamodb = self.get_dynamodb_client(request)
        response = self.get_billings(dynamodb, b_account_id, is_current_month)
        items = response['Items']
        response = HttpResponse(content_type='text/csv')
        response['content-disposition'] = 'attachment; filename="account{}_{}-{}_bill.csv"'.format(b_account_id, str(datetime.now().year), str(datetime.now().month))
        writer = csv.writer(response)
        writer.writerow(['服务', '使用类型', '单价折扣', '用量', '计价单位', '费用'])  # 写入表头
        for item in items:
            writer.writerow([item['product_product_name'], item['line_item_usage_type'], item['line_item_line_item_description'], item['usage_quantity'], item['pricing_unit'], item['cost']])
        return response


