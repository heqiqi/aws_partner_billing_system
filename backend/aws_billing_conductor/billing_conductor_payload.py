from drf_yasg import openapi

delete_group_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                   required=['Arn'],
                                   properties={
                                       'Arn': openapi.Schema(type=openapi.TYPE_STRING, description='AWS Arn')})

create_group_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                   required=['name', 'checkedAccount', 'checkedPrimaryAccount',
                                             'isCreatePlan'],
                                   properties={
                                       'name': openapi.Schema(type=openapi.TYPE_STRING, description='AWS Arn'),
                                       'isCreatePlan': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                      description='The set of accounts'),
                                       'checkedAccount': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                        items=openapi.Items(
                                                                            type=openapi.TYPE_STRING),
                                                                        description='checkedAccount'),
                                       'checkedPrimaryAccount': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description='Account Id'),
                                   })

create_price_rule = openapi.Schema(type=openapi.TYPE_OBJECT,
                                   required=['name', 'checkedAccount', 'checkedPrimaryAccount',
                                             'isCreatePlan'],
                                   properties={
                                       'name': openapi.Schema(type=openapi.TYPE_STRING, description='AWS Arn'),
                                       'discount': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Discount'),
                                   })

create_pricing_rule_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          required=['Name', 'Scope', 'Type', 'ModifierPercentage'],
                                          properties={
                                              'Name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     description='AWS Arn'),
                                              'AccountGrouping': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                                description='The set of accounts'),
                                              'ComputationPreference': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                                      description='PricingPlanArn'),
                                              'PrimaryAccountId': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                 description='Account Id'),
                                          })

create_pricing_plan_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          required=['Name'],
                                          properties={
                                              'Name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     description='Plan name'),
                                              'Description': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            description='Description'),
                                              'PricingRuleArns': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                                items=openapi.Items(
                                                                                    type=openapi.TYPE_STRING),
                                                                                description='PricingPlanArn'),
                                          })

update_bill_group = openapi.Schema(type=openapi.TYPE_OBJECT,
                                   required=['Arn', 'ComputationPreference'],
                                   properties={
                                       'Arn': openapi.Schema(type=openapi.TYPE_STRING,
                                                             description='AWS Arn'),
                                       'ComputationPreference': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                               description='PricingPlanArn'),
                                   })

invite_account = openapi.Schema(type=openapi.TYPE_OBJECT,
                                required=['Id', 'Type'],
                                properties={
                                    'Id': openapi.Schema(type=openapi.TYPE_STRING, description='AWS Id'),
                                    'Type': openapi.Schema(type=openapi.TYPE_STRING, description='Type'),
                                })

create_account = openapi.Schema(type=openapi.TYPE_OBJECT,
                                required=['Email', 'AccountName'],
                                properties={
                                    'Email': openapi.Schema(type=openapi.TYPE_STRING, description='root email'),
                                    'AccountName': openapi.Schema(type=openapi.TYPE_STRING, description='Account Name'),
                                })

org_attach_policies = openapi.Schema(type=openapi.TYPE_OBJECT,
                                required=['TargetId', 'PolicyId'],
                                properties={
                                    'TargetId': openapi.Schema(type=openapi.TYPE_STRING, description='account arn'),
                                    'PolicyId': openapi.Schema(type=openapi.TYPE_STRING, description='Policy Id'),
                                })

close_account = openapi.Schema(type=openapi.TYPE_OBJECT,
                                required=['AccountId'],
                                properties={
                                    'AccountId': openapi.Schema(type=openapi.TYPE_STRING, description='account Id'),
                                })

mail_payload = openapi.Schema(type=openapi.TYPE_OBJECT,
                                required=['recipient', 'subject', 'body'],
                                properties={
                                    'recipient': openapi.Schema(type=openapi.TYPE_STRING, description='mail  recipient'),
                                    'subject': openapi.Schema(type=openapi.TYPE_STRING, description='mail  subject'),
                                    'body': openapi.Schema(type=openapi.TYPE_STRING, description='mail  body')
                                })
