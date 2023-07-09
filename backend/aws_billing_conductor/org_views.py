import boto3
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
import logging

from aws_billing_conductor.billing_conductor_payload import invite_account, create_account, org_attach_policies, \
    mail_payload, close_account
from dvadmin.system.models import Dept
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def getAccountIdFromRequest(request):
    param = request.GET.copy()
    accId = param.get('account_id', None)
    logger.info("account_id: {}".format(accId))
    return accId


class AwsOrganizationViewSet(ViewSet):

    def getAwsClient(self, request):
        ak = request.user.dept.access_key if request.user.dept is not None else None
        sk = request.user.dept.secret_key if request.user.dept is not None else None
        accId = getAccountIdFromRequest(request)
        if accId is not None:
            dept = Dept.objects.filter(account_id=accId)
            ak = dept[0].access_key
            sk = dept[0].secret_key
        return boto3.client('organizations',
                            aws_access_key_id=ak,
                            aws_secret_access_key=sk,
                            region_name='us-east-1')

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def accounts(self, request):
        """
        listAccounts
        """
        client = self.getAwsClient(request)
        accountList = client.list_accounts()
        logger.info('{}'.format(accountList))
        return DetailResponse(accountList[u'Accounts'])

    @swagger_auto_schema(method='post', request_body=invite_account)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def invite_account(self, request):
        """
        inviteAccount
        """
        client = self.getAwsClient(request)
        invite = client.invite_account_to_organization(
            Target={
                'Id': request.data['Id'],
                'Type': request.data['Type']
            }
        )
        logger.info('{}'.format(invite))
        del invite['ResponseMetadata']
        return DetailResponse(invite)

    @swagger_auto_schema(method='post', request_body=create_account)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_account(self, request):
        """
        inviteAccount
        post data example:
        {
            "Email": "qihen+cli@amazon.com",
             "AccountName": "qihenTestBilling"
        }
        """
        logger.info('{}'.format(request.data))
        client = self.getAwsClient(request)
        resp = client.create_account(
            **{
                'Email': request.data['Email'],
                'AccountName': request.data['AccountName']
            }
        )
        logger.info('{}'.format(resp))
        del resp['ResponseMetadata']
        return DetailResponse(resp)


    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def list_policies(self, request):
        """
        listPolicies
        """
        client = self.getAwsClient(request)
        resp = client.list_policies(**{
            'Filter': 'SERVICE_CONTROL_POLICY'
        })
        logger.info('list_policies:{}'.format(resp))
        del resp['ResponseMetadata']
        return DetailResponse(resp)

    @swagger_auto_schema(method='get',
                         manual_parameters=[openapi.Parameter('TargetId', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
                         request_body=None)
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def list_policies_for_target(self, request):
        """
        listPoliciesForTarget
        """
        client = self.getAwsClient(request)
        resp = client.list_policies_for_target(**{
            'TargetId': request.GET.copy().get('TargetId', None),
            'Filter': 'SERVICE_CONTROL_POLICY'
        })
        logger.info('list_policies_for_target:{}'.format(resp))
        del resp['ResponseMetadata']
        return DetailResponse(resp)

    @swagger_auto_schema(method='post',request_body=org_attach_policies)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def attach_policy(self, request):
        """
        attach_policy
        """
        client = self.getAwsClient(request)
        resp = client.attach_policy(**{
            'TargetId': request.data['TargetId'],
            'PolicyId': request.data['PolicyId']
        })
        logger.info('attach_policy:{}'.format(resp))
        del resp['ResponseMetadata']
        return DetailResponse(resp)

    @swagger_auto_schema(method='post', request_body=org_attach_policies)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def detach_policy(self, request):
        """
        attach_policy
        """
        client = self.getAwsClient(request)
        resp = client.detach_policy(**{
            'TargetId': request.data['TargetId'],
            'PolicyId': request.data['PolicyId']
        })
        logger.info('detach_policy:{}'.format(resp))
        del resp['ResponseMetadata']
        return DetailResponse(resp)

    @swagger_auto_schema(method='post', request_body=close_account)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def close_account(self, request):
        """
        close_account
        """
        logger.info("{}".format("close_account"))
        client = self.getAwsClient(request)
        resp = client.close_account(**{
            'AccountId': request.data['AccountId']
        })
        logger.info('close_account:{}'.format(resp))
        del resp['ResponseMetadata']
        return DetailResponse(resp)

    @swagger_auto_schema(method='post', request_body=mail_payload)
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def send_notification(self, request):
        logger.info("{}".format("send_notificatoin"))
        result = send_mail(
            request.data['subject'],
            request.data['body'],
            'notify_noreply@yeah.net',
            [request.data['recipient']],
            fail_silently=False,
        )
        logger.info("{}: {}".format("send_notificatoin complete",result))
        return SuccessResponse()








