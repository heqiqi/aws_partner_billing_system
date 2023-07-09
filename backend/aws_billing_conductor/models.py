from django.db import models

# Create your models here.
# Create your models here.
from dvadmin.utils.models import CoreModel


class AwsBillingConductorGroupModel(models.Model):
    name = models.CharField(max_length=255, verbose_name="名字")
    size = models.IntegerField(verbose_name="数量")
    arn = models.CharField(max_length=255,verbose_name="arn")
    creation_time = models.DateField(verbose_name="创建时间")

    class Meta:
        db_table = "billing_conductor_group"
        verbose_name = '账单组表'
        verbose_name_plural = verbose_name
        ordering = ('creation_time',)
