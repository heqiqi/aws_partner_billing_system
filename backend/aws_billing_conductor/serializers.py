from aws_billing_conductor.models import AwsBillingConductorGroupModel
from dvadmin.utils.serializers import CustomModelSerializer


class AwsBillingConductorGroupModelSerializer(CustomModelSerializer):
    """
    序列化器
    """

    class Meta:
        model = AwsBillingConductorGroupModel
        fields = "__all__"


class AwsBillingConductorGroupModelCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新时的列化器
    """

    class Meta:
        model = AwsBillingConductorGroupModel
        fields = '__all__'
