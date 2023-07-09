import boto3


class AwsCliService:
    def __init__(self, ak, sk):
        self.ak = sk
        self.sk = sk
        self.client = boto3.client('billingconductor',
                                   aws_access_key_id=ak,
                                   aws_secret_access_key=sk,
                                   region_name='us-east-1')

    def get_client(self):
        return self.client

    def list_pricing_rules(self, kwargs):
        """
        listPricingRules
        """
        pricingRuleList = self.client.list_pricing_rules(**kwargs)
        return pricingRuleList[u'PricingRules']

    def list_pricing_plans(self, kwargs):
        """
        listPricingPlans
        """
        pricingPlanList = self.client.list_pricing_plans(**kwargs)
        return pricingPlanList[u'PricingPlans']

    def get_bill_group_list(self, kwargs):
        """
        getBillgroupList
        """
        groupList = self.client.list_billing_groups(**kwargs)
        return groupList[u'BillingGroups']

    def list_billing_group_cost_reports(self, kwargs):
        groupList = self.client.list_billing_group_cost_reports(**kwargs)
        return groupList[u'BillingGroupCostReports']

    def delete_billing_group(self, kwargs):
        """
        deleteBillingGroup
        """
        groupList = self.client.delete_billing_group(**kwargs)
        return groupList

    def list_account_associations(self, kwargs):
        """
        listAccountAssociations
        """
        assocList = self.client.list_account_associations(**kwargs)
        return assocList[u'LinkedAccounts']

    def create_billing_group(self, kwargs):
        """
        create_billing_group
        """
        bgroup = self.client.create_billing_group(**kwargs)
        return bgroup

    def create_pricing_rule(self, kwargs):
        """
        create_pricing_rule
        """
        prule = self.client.create_pricing_rule(**kwargs)
        return prule

    def create_pricing_plan(self, kwargs):
        """
        create_pricing_plan
        """
        pplan = self.client.create_pricing_plan(**kwargs)
        return pplan

    def update_billing_group(self, kwargs):
        """
        update_billing_group
        """
        bgroup = self.client.update_billing_group(**kwargs)
        del bgroup['ResponseMetadata']
        return bgroup

    def list_custom_line_items(self, kwargs):
        groupList = self.client.list_custom_line_items(**kwargs)
        return groupList[u'CustomLineItems']

    def delete_custom_line_items(self, kwargs):
        resp = self.client.delete_custom_line_item(**kwargs)
        del resp['ResponseMetadata']
        return resp

    def create_custom_line_item(self, kwargs):
        resp = self.client.create_custom_line_item(**kwargs)
        del resp['ResponseMetadata']
        return resp

    def batch_disassociate_resources_from_custom_line_item(self, kwargs):
        resp = self.client.batch_disassociate_resources_from_custom_line_item(**kwargs)
        del resp['ResponseMetadata']
        return resp

    def disassociate_accounts(self, kwargs):
        resp = self.client.disassociate_accounts(**kwargs)
        del resp['ResponseMetadata']
        return resp

    def associate_accounts(self, kwargs):
        resp = self.client.associate_accounts(**kwargs)
        del resp['ResponseMetadata']
        return resp

    def list_pricing_rules_associated_to_pricing_plan(self, kwargs):
        resp = self.client.list_pricing_rules_associated_to_pricing_plan(**kwargs)
        del resp['ResponseMetadata']
        return resp

    def list_pricing_rules(self, kwargs):
        resp = self.client.list_pricing_rules(**kwargs)
        del resp['ResponseMetadata']
        return resp