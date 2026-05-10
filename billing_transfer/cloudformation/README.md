# CloudFormation 模版说明

本目录包含 4 个 CloudFormation 模版，用于支持 **AWS Partner Central 渠道管理（Channel Management）** 与 **账单转移（Billing Transfer）** 场景，并在账单转移激活后自动创建每个客户的 CUR（Cost and Usage Report）数据导出。

模版可分为两类：

1. **权限 / 角色类**（`apnlinked-role.yaml`、`pma-roles.yaml`）——为 Partner Central 渠道管理创建所需的 IAM 角色。
2. **账单自动化类**（`disti-cma-cur.yaml`、`spp-cma-cur.yaml`）——监控账单转移激活状态并自动创建每客户 CUR。

---

## 1. `apnlinked-role.yaml`

**用途：** 在 **Partner Central Linked Account（APN 关联账户）** 中创建渠道管理角色。

| 项目 | 说明 |
| --- | --- |
| 部署位置 | **仅** Partner Central Linked（APN 关联）账户 |
| 创建资源 | IAM 角色 `PartnerCentralRoleForChannel` |
| 信任主体 | `partnercentral-account-management.amazonaws.com` |
| 附加策略 | 托管策略 `AWSPartnerCentralChannelManagement` |
| 作用 | 让 Partner Central 用户能够访问并管理 PMA（Program Management Account）渠道管理功能 |

**后续步骤：** 部署后，需在每个 PMA 中部署 `pma-roles.yaml`，再通过 Partner Central 控制台将 IAM 角色映射给对应用户。

---

## 2. `pma-roles.yaml`

**用途：** 在 **Program Management Account（PMA）** 中创建渠道管理与账单转移所需的角色。

| 项目 | 说明 |
| --- | --- |
| 部署位置 | **仅** Program Management Account（PMA） |
| 关键参数 | `PartnerCentralLinkedAccountId`（12 位 APN 关联账户 ID）、`EnableBillingTransferManagement`（是否创建可选管理角色） |

创建的角色：

- **`PartnerCentralChannelHandshakeApprovalManagement`** — 处理 Partner Central 与本账户之间的握手（handshake），用于激活 PMA。信任 `partnercentral-account-management.amazonaws.com`，附加 `AWSPartnerCentralChannelHandshakeApprovalManagement` 托管策略。
- **`PartnerCentralChannelBillingTransferReadOnly`** — 跨账户只读角色，供 APN 关联账户假设，用于从 Partner Central 查看账单转移状态（`organizations:Describe/List*ResponsibilityTransfer*` 等只读权限）。
- **`PartnerCentralChannelBillingTransferManagement`** *(可选)* — 仅当 `EnableBillingTransferManagement=true` 时创建。启用 Partner Central 中的 "Manage in AWS Billing" 按钮，允许直接在 Partner Central 创建 / 管理账单转移（含 `organizations:Accept/Decline/CancelHandshake`、`InviteOrganizationToTransferResponsibility`、`billingconductor:*` 等写权限）。

**后续步骤：** 部署后前往 Partner Central 渠道管理，将本账户创建并激活为 PMA。

---

## 3. `disti-cma-cur.yaml`

**用途：** 账单转移激活监控 + 自动 CUR 创建，面向 **分销（Distribution）/ 三层（three-tier）** 模式。

| 项目 | 说明 |
| --- | --- |
| 部署位置 | **必须部署在 `us-east-1`** |
| 适用模型 | 直接（direct）关系 与 三层分销关系 |
| 关键参数 | `AlertEmail`、`S3BucketPrefix`、`BillingViewType`（`MY_VIEW` 标准账单 / `SHOWBACK_CHARGEBACK_VIEW` 三层 + Billing Conductor 账单组）、`ActivationCheckCron`、`CURCreationSchedule`，以及可选的 `MSTeamsWebhookUrl`、`LineNotifyToken` 通知 |

**工作方式：**
- 定时检查账单转移是否激活（默认每月 1 日 00:03 UTC）。
- 检测到激活后，为每个客户创建独立的 S3 存储桶（`{prefix}-cur-{account_id}`）及 BCM Data Export（CUR）。
- 通过邮件（及可选的 MS Teams / Line）发送通知。
- 使用 `SHOWBACK_CHARGEBACK_VIEW` 时，需在创建 CUR 前先存在对应的 Billing Conductor 账单组。
- 内置自包含的 boto3 Lambda Layer 构建器，无外部依赖。

---

## 4. `spp-cma-cur.yaml`

**用途：** 账单转移激活监控 + 自动 CUR 创建，面向 **SPP 两层（Solution Provider → Customer）** 模式。

| 项目 | 说明 |
| --- | --- |
| 部署位置 | **必须部署在 `us-east-1`** |
| 适用模型 | SPP 两层模式（Solution Provider Program） |
| 关键参数 | `AlertEmail`、`S3BucketPrefix`、`ActivationCheckCron`、`CURCreationSchedule`，以及可选的 `MSTeamsWebhookUrl`、`LineNotifyToken` 通知 |

**工作方式：** 与 `disti-cma-cur.yaml` 逻辑基本一致（定时检测激活 → 每客户建桶 + 建 CUR → 通知），但针对 SPP 两层场景做了简化，**不包含** `BillingViewType` 参数（无三层 / Billing Conductor 分支）。

---

## 典型部署流程

1. 在 **APN 关联账户** 部署 `apnlinked-role.yaml`。
2. 在每个 **PMA** 部署 `pma-roles.yaml`（填入 APN 关联账户 ID，按需开启管理角色）。
3. 在 Partner Central 完成 PMA 激活与用户角色映射。
4. 根据业务模型，在 **`us-east-1`** 部署账单自动化模版：
   - 分销 / 三层 → `disti-cma-cur.yaml`
   - SPP 两层 → `spp-cma-cur.yaml`

> **注意：** 两个 CUR 模版都必须部署在 `us-east-1` 区域。
