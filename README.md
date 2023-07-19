# 伙伴账单系统介绍
AWS伙伴账单系统是一种高效的财务管理工具，通过采用API形式管理组织和账单，为AWS伙伴提供了便利的、高效的和可扩展的方式来管理其云资源和费用。该系统实现了基本功能程序化的管理，以实现最大的效率和精度。
主要有如下功能：
* 账单管理
    - 账单组管理
    - 账单折扣管理
    - 附加费用管理

* 组织管理
    - Linked Account创建
    - Linked Account邀请
    - Linked Account权限控制
    - 信息邮件通知
    - 账户关闭

* 组织账单洞察
    - 组织级费用可视化
    - 分类用量展示
    - MoM对比

* Payer管理
    - Admin管理多Payer账号
    - 单Payer管理员

## 账单管理系统架构
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/sytem-arch.png)

## 部分截图
- 组织费用概览
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/Screenshot1.png)
- 账单组管理
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/Screenshot2.png)
- 组织管理
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/Screenshot3.jpeg)


## 部署步骤
### Dashboard部署
- 参考 [Cost Intelligent Dashiboard](https://www.wellarchitectedlabs.com/cost/200_labs/200_cloud_intelligence/cost-usage-report-dashboards/dashboards/deploy_dashboards/)，创建Dashboard
    * cloudformation的参数
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/dashboard-cfn.png)
- 设置QuickSight看板共享
    * 进入QuickSight的Cost Intelligent Dashboard
    * 点击共享，设置为public，并记录下embed code
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/set-share.png)
    * 设置域名访问权限:
    ```在QuickSight右上角，点击"Manage QuickSight",在左侧点击“Domains and Embedding”```
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/domains-permission.png)
     
### 组织配置部署
- 设置Stackset,在每个Linked的账户内开启Cost Usage Report，并将parque格式的CUR保存在link账号S3 Bucket内
    * 修改`cloudformation/Cur-S3.template.yml`， 将`<payer account Id>`替换为payer accound Id
    * 在Cloudformation 控制台，点击创建新的StackSet，选择us-east-1 region，选择所有linked account，然后使用模版`cloudformation/Cur-S3.template.yml`创建。
- 设置Lambda function，同步复制CUR到Payer S3 Bucket
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/OCA-Billing-System-Arch.png)
    * 设置新的lambda execution role，命名为：`Lambda-List-S3-Role`， role 的权限如下
        * 内置权限
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Sid": "S3ListBucket",
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket"
                        ],
                        "Resource": "arn:aws:s3:::org-lead-cur-*"
                },
                {
                    "Sid": "logsstreamevent",
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:us-east-1:<payer account Id>:log-group:/aws/lambda/Lambda-List-S3*/*"
                },
                {
                    "Sid": "logsgroup",
                    "Effect": "Allow",
                    "Action": "logs:CreateLogGroup",
                    "Resource": "*"
                }
                ]
            }            
            ```
        * 托管权限
        ![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/permission-lambda.png)
    * 创建Lambda function，源码为: `lambda/cpy_linked_s3_to_payer.py`, 执行role使用`Lambda-List-S3-Role`
    * 使用EventBridge设置cronjob rule，设置为UTC时间2:00

- 设置Glue Crawler，定时使用新的CUR，更新Database
    * Crawler 命名为：`cur_crawler_<linked account Id>`
    * Glue Catalog Database 命名为：`monthly-cur-<linked account Id>`
    * Crawler 爬取S3路径为：`s3://org-cur-integration-<payer account Id>/<linked account Id>/monthly`
    * Crawler 定时执行，执行时间为UTC时间2:30
- 设置Lambda function，每天将解析后的用量报告同步到DynamoDB
    * 新建Lambda函数，Execution Role仍然为：`Lambda-List-S3-Role`
    * 函数源代码为：`lambda/athena_query_lambda.py`
    * 新建EventBridge Rule，将 Glue crawler的完成状态作为 event，此lambda函数作为target。
      event pattern:
      ```
      {
          "source": [
          "aws.glue"
      ],
      "detail-type": [
        "Glue Crawler State Change"
      ],
      "detail": {
        "state": [
          "Succeeded"
        ]
      }
    }
    ```
    * 使用上一步创建的EventBridge Rule 做为trigger，在crawler完成是启动lambda。
### 管理后台部署
- 前端部署
    * 进入`web`文件夹
    * 安装node.js， nodejs >= 16.0
    * 安装依赖库文件`npm install`
    * 执行编译`npm run build`
    * `dist`文件夹下问前端部署文件。可以根据实际情况，在nignx或S3部署

- 后端部署
    * 进入`backend`文件夹
    * 安装pyhton3， Python >= 3.8.0
    * pip3 install -r requirements.txt
    * 启动后端服务，2种方式：
        * `python3 manage.py runserver 0.0.0.0:8000`
        * `gunicorn -c gunicorn_conf.py application.asgi:application`
    * 根据部署方式，将/api/*的请求路由到正确后端服务
    * 如需使用邮件通知服务，请配置`backend/application/settings.py`中的“smpt服务器地址”
## 首次设置
### 设置后台
首次登录的管理员用户名：superadmin，密码为：admin123456
- 登录aws console，在 payer 账号下，创建新的IAM User， 并且生成AK、SK，所需权限如下：
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/payer-iam-permission.png)

- 创建组织账号，并录入account Id、AK、SK，以及dashboard链接。
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/step1.png)

- 创建新用户，关联到对应组织。
![image](https://github.com/heqiqi/aws_partner_billing_system/blob/main/data/img/step2.png)

### 设置组织SCP策略
为了能控制linked account的权限，需要在[aws organizaton console]()创建scp策略，常用策略请[点击](https://monkey16.notion.site/scp-5a73963ac1bb42e08d5ead235aa649d1?pvs=4)

## 参考资料
- admin框架，[django-vue-admin](https://github.com/liqianglog/django-vue-admin)
- Python AWS SDK，[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
- 账单管理服务， [Billing Conductor](https://docs.aws.amazon.com/billingconductor/latest/userguide/what-is-billingconductor.html)
