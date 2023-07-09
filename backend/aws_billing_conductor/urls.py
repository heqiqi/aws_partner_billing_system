from rest_framework.routers import SimpleRouter
from django.urls import path
from .billing_views import AwsBillingConductorGroupModelViewSet
from .org_views import AwsOrganizationViewSet

router = SimpleRouter()
router.register("api/aws/billing_group", AwsBillingConductorGroupModelViewSet, basename='billing')
router.register("api/aws/organization", AwsOrganizationViewSet, basename='organization')

urlpatterns = [
    # path("api/aws_billing_group", InviteAccountToOrganization.as_view(), name='invite-account'),
]
urlpatterns += router.urls
