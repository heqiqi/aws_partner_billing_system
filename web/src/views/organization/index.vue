<template>
  <d2-container>
  <div style="color: #909399">
    组织账号
    <el-select v-model="selectedAccount" placeholder="请选择"  style="margin-left: 1rem">
      <el-option
        v-for="(item, index) in accountList"
        :key="item.account_id"
        :label="item.name"
        :value="index">
      </el-option>
    </el-select>
  </div>
  <hr>
  <el-card v-loading="!showEchart">
<!--    <div slot="header" class="clearfix">-->
<!--      <span>组织成员</span>-->
<!--    </div>-->
    <el-table
      :data="accountGroup"
      stripe
      border
      style="width: 100%">
      <el-table-column
        prop="Name"
        label="账户名"
        width="180">
      </el-table-column>
      <el-table-column
        prop="Id"
        label="账号Id"
        width="120">
      </el-table-column>
      <el-table-column
        prop="Email"
        label="邮箱"
        width="180">
      </el-table-column>
      <el-table-column
        prop="JoinedMethod"
        label="加入方式"
        width="120">
      </el-table-column>
      <el-table-column
        prop="Status"
        label="当前状态"
        width="120">
      </el-table-column>
      <el-table-column
        align="center"
        label="操作"
        width="80">
        <template slot-scope="scope">
          <el-button
            @click="permissionAcc(scope.row)"
            type="text"
            size="small">
            权限
          </el-button>
          <el-button
            @click="billDetail(scope.row)"
            type="text"
            style="color: #409EFF;"
            size="small">
            账单
          </el-button>
          <el-button
            @click="emailNotify(scope.row)"
            type="text"
            style="color: #409EFF;"
            size="small">
            通知
          </el-button>
<!--          <el-popover-->
<!--            placement="top"-->
<!--            width="160"-->
<!--            v-model="closeAccountvisible">-->
<!--            <p>关闭后不可恢复，确定关闭账户？</p>-->
<!--            <div style="text-align: right; margin: 0">-->
<!--              <el-button size="mini" type="text" @click="closeAccountvisible = false">取消</el-button>-->
<!--              <el-button type="primary" size="mini" @click="closeAccount(scope.row)">确定</el-button>-->
<!--            </div>-->
<!--            <el-button-->
<!--              slot="reference"-->
<!--              type="text"-->
<!--              style="color: #409EFF;"-->
<!--              size="small">-->
<!--              关闭-->
<!--            </el-button>-->
<!--          </el-popover>-->
          <el-button
            @click="closeAccount(scope.row)"
            type="text"
            style="color: #409EFF;"
            size="small">
            关闭
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <br>
    <div>
      <el-button style="float: right; margin-right: 5vw; margin-bottom: 16px;" type="success" @click="showCreateAccDialog(false)" size="small"  icon="el-icon-plus">邀请</el-button>
      <el-button style="float: right; margin-right: 2vw; margin-bottom: 16px;" type="primary" @click="showCreateAccDialog(true)" size="small"  icon="el-icon-plus">新增</el-button>
    </div>
  </el-card>
  <el-dialog title="添加账户" :visible.sync="showOrgAccountCreator" >
      <el-form :model="orgAccountForm" style="width: 85%;" v-loading="!showDialog">
        <el-form-item label="邀请类型" :label-width="formLabelWidth" prop="Type" v-if="!this.isCreateNewAccount">
          <el-select v-model="orgAccountForm.Type" placeholder="请选择类型">
            <el-option v-for="bg in this.accOptions" :label="bg.label"  :value="bg.value" :key="bg.value">{{bg.label}}</el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="账户信息"  prop="Id" :label-width="formLabelWidth" v-if="!this.isCreateNewAccount">
          <el-input v-model="orgAccountForm.Id" ></el-input>
        </el-form-item>
        <el-form-item label="注册邮箱"  prop="Email" :label-width="formLabelWidth" v-if="this.isCreateNewAccount">
          <el-input v-model="orgAccountForm.Email" ></el-input>
        </el-form-item>
        <el-form-item label="用户名"  prop="AccountName" :label-width="formLabelWidth" v-if="this.isCreateNewAccount">
          <el-input v-model="orgAccountForm.AccountName" ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showOrgAccountCreator = false">取 消</el-button>
        <el-button type="primary" @click="doCreateAccount">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog title="账户权限" :visible.sync="showPoliciesDialog" >
        <el-table
          v-loading="this.policiesLoading"
          :data="this.policiesList"
          stripe
          style="width: 100%">
          <el-table-column
            prop="Name"
            label="名称"
            width="180">
          </el-table-column>
          <el-table-column
            prop="Description"
            label="描述"
            width="180">
          </el-table-column>
          <el-table-column
            align="center"
            label="操作"
            width="80">
            <template slot-scope="scope">
              <el-switch
                v-model="scope.row.switch"
                active-color="#13ce66"
                inactive-color="#ff4949"
                @change="changeOnSwitchBtn(scope.row)">
              </el-switch>
            </template>
          </el-table-column>
        </el-table>
    </el-dialog>

    <el-dialog title="服务升级通知" :visible.sync="emailFormVisible">
      <el-form :model="emailForm" label-position="top">
        <el-form-item label="收件人" :label-width="emailLabelWidth">
          <el-input v-model="emailForm.recipient" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="主题" :label-width="emailLabelWidth">
          <el-input v-model="emailForm.subject" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="内容" :label-width="emailLabelWidth">
          <el-input v-model="emailForm.body"  type="textarea" :rows="5"  autocomplete="off"></el-input>
        </el-form-item>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="emailFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="sendMail()">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog title="账单详情" :visible.sync="billTableVisible" width="80%">
      <el-table :data="billItems" v-loading="loadingBillData">
        <el-table-column property="product_product_name" label="产品" width="160"></el-table-column>
        <el-table-column property="line_item_usage_type" label="种类" width="170"></el-table-column>
        <el-table-column property="line_item_line_item_description" label="单价" width="180"></el-table-column>
        <el-table-column property="usage_quantity" label="用量" width="40"></el-table-column>
        <el-table-column property="pricing_unit" label="单位" width="40"></el-table-column>
        <el-table-column property="cost" label="费用" width="40"></el-table-column>
      </el-table>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="downloadCsv()">下 载</el-button>
      </div>
    </el-dialog>

    <el-dialog
      title="提示"
      :visible.sync="closeAccountvisible"
      width="30%"
      center>
      <span>账户关闭后不可恢复，确定关闭？</span>
      <span slot="footer" class="dialog-footer">
    <el-button @click="closeAccountvisible = false">取 消</el-button>
    <el-button type="primary" @click="doCloseAccount()">确 定</el-button>
  </span>
    </el-dialog>

  </d2-container>
</template>

<script>
import CsvExportor from 'csv-exportor'
import { createAccountToOrg, GetAccountList, inviteAccountToOrg } from '@/views/billgroup/api'
import {
  attachPolicy, closeAccountApi,
  detachPolicy, GetBillItems,
  GetPoliciesList,
  GetPoliciesListForTarget,
  sendMailApi
} from '@/views/organization/api'
import { request } from '@/api/service'

export default {
  name: 'organization',
  data () {
    return {
      selectedAccount: 0,
      accountList: [],
      showEchart: false,
      pieData: [],
      legendData: ['aws cost'],
      deleteDialogVisible: false,
      myChart: null,
      countAccount: 0,
      accountGroup: [],
      showOrgAccountCreator: false,
      isCreateNewAccount: false,
      showDialog: true,
      orgAccountForm: {},
      formLabelWidth: '120px',
      emailLabelWidth: '80px',
      accOptions: [{
        value: 'EMAIL',
        label: '注册邮箱'
      }, {
        value: 'ACCOUNT',
        label: 'AWS ID'
      }],
      policiesList: [],
      showPoliciesDialog: false,
      policiesLoading: true,
      emailFormVisible: false,
      emailForm: {},
      billTableVisible: false,
      loadingBillData: false,
      billItems: [],
      closeAccountvisible: false,
      readyTodeleteAccount: {}
    }
  },
  watch: {
    selectedAccount (newValue, oldValue) {
      console.log('selectedAccount', newValue, 'oldValue', oldValue, ' ', JSON.stringify(this.$store.state.d2admin.billgroup.accountDetails), ' test ', this.$store.state.d2admin.billgroup.selectedAccount)
      if (newValue !== oldValue) {
        this.showEchart = false
        this.accountGroup = []
        this.accountInOrgRequest({ account_id: this.accountList[this.selectedAccount].account_id })
        this.$store.commit('d2admin/billgroup/modify', newValue)
        this.$store.commit('d2admin/billgroup/account', this.accountList[newValue])
      }
    }
  },
  methods: {
    GetDeptList (query) {
      return request({
        url: '/api/system/menu/dashboard_url/',
        method: 'get',
        params: query
      })
    },
    async accountInOrgRequest (query) {
      const account = await GetAccountList(query)
      console.log(JSON.stringify(account))
      this.accountGroup = account.data
      this.showEchart = true
    },
    async changeOnSwitchBtn (policy) {
      console.log(JSON.stringify(policy), this.targeId)
      this.policiesLoading = true
      if (policy.switch) {
        console.log('attach policy: ' + policy.Id)
        await attachPolicy({ PolicyId: policy.Id, TargetId: this.targeId }, { account_id: this.accountList[this.selectedAccount].account_id })
      } else {
        await detachPolicy({ PolicyId: policy.Id, TargetId: this.targeId }, { account_id: this.accountList[this.selectedAccount].account_id })
      }
      this.policiesLoading = false
    },
    async policyListRequest (query) {
      const policies = await GetPoliciesList(query)
      const targetPolicy = await GetPoliciesListForTarget(query)
      this.policiesList = policies.data.Policies.map(item => {
        item.switch = this.hasKeyVaule(targetPolicy.data.Policies, 'Id', item.Id)
        return item
      })
      console.log(JSON.stringify(this.policiesList))
    },
    hasKeyVaule (array, key, value) {
      return array.some(obj => {
        return Object.keys(obj).some(keyName => {
          return keyName === key && obj[keyName] === value
        })
      })
    },
    showCreateAccDialog (isCreate) {
      this.isCreateNewAccount = isCreate
      this.showOrgAccountCreator = true
    },
    async doCreateAccount () {
      console.log(JSON.stringify(this.orgAccountForm))
      this.showDialog = false
      try {
        if (this.isCreateNewAccount) {
          console.log('create new account')
          await createAccountToOrg(this.orgAccountForm, { account_id: this.accountList[this.selectedAccount].account_id })
        } else {
          console.log('invite old account')
          await inviteAccountToOrg(this.orgAccountForm, { account_id: this.accountList[this.selectedAccount].account_id })
        }
        this.showEchart = false
        console.log('create new account1')
        await this.accountInOrgRequest({ account_id: this.accountList[this.selectedAccount].account_id })
        console.log('create new account2')
        this.$message({
          message: '成功',
          type: 'success'
        })
        this.showOrgAccountCreator = false
      } catch (e) {
        console.log(e)
        this.$message({
          message: '失败',
          type: 'error'
        })
      } finally {
        this.showDialog = true
      }
    },
    async permissionAcc (target) {
      if (target.Status !== 'ACTIVE') {
        this.$message({
          message: '此账号已停用',
          type: 'error'
        })
        return
      }
      this.showPoliciesDialog = true
      this.policiesLoading = true
      this.targeId = target.Id
      this.policiesList = []
      await this.policyListRequest({ account_id: this.accountList[this.selectedAccount].account_id, TargetId: this.targeId })
      this.policiesLoading = false
    },
    async billDetail (account) {
      this.billTableVisible = true
      this.loadingBillData = true
      try {
        this.$message({
          message: '发送中...',
          type: 'info'
        })
        const response = await GetBillItems({ account_id: this.accountList[this.selectedAccount].account_id, bill_account_id: account.Id })
        console.log('billDetail ' + JSON.stringify(response))
        // {
        //   "cost": "0.17",
        //   "bill_payer_account_id": "227976579875",
        //   "line_item_line_item_description": "$0.0416 per On Demand Linux t3.medium Instance Hour (-80.00%)",
        //   "usage_quantity": "21.0",
        //   "createAt": 1688275363168,
        //   "account_month": "227976579875_7",
        //   "product_product_name": "Amazon Elastic Compute Cloud",
        //   "pricing_unit": "Hrs",
        //   "product_usage_type_quantity": "Amazon Elastic Compute CloudBoxUsage:t3.medium227976579875",
        //   "line_item_usage_type": "BoxUsage:t3.medium"
        // }
        this.billItems = response.data
      } catch (e) {
        console.log(e)
        this.$message({
          message: '  获取失败',
          type: 'error'
        })
      } finally {
        this.loadingBillData = false
      }
    },
    async downloadCsv () {
      if (this.billItems.length === 0) {
        this.$message({
          message: '无账单详情',
          type: 'error'
        })
        return
      }
      try {
        const tableData = []
        for (let n = 0; n < this.billItems.length; n++) {
          // const i = this.billItems[n]
          console.log('billItems: ' + JSON.stringify(this.billItems[n]))
          tableData.push({ a: this.billItems[n].product_product_name, b: this.billItems[n].line_item_usage_type, c: this.billItems[n].line_item_line_item_description, ab: this.billItems[n].usage_quantity, e: this.billItems[n].pricing_unit, d: '$' + this.billItems[n].cost })
        }
        console.log('csvdata: ' + JSON.stringify(tableData))
        const now = new Date()
        const year = now.getFullYear()
        const month = now.getMonth() + 1
        const header = ['服务', '使用类型', '单价折扣', '用量', '计价单位', '费用']
        CsvExportor.downloadCsv(tableData, { header }, 'account:' + this.billItems[0].bill_payer_account_id + '_' + year + '_' + month + '_bill.csv')
      } catch (e) {
        console.log(e)
        this.$message({
          message: '  获取失败',
          type: 'error'
        })
      } finally {
        this.loadingBillData = false
      }
    },
    emailNotify (account) {
      console.log('in emailFormVisible')
      this.$set(this.emailForm, 'recipient', account.Email)
      this.$set(this.emailForm, 'subject', '请填写邮件主题，比如：EKS、RDS升级')
      this.$set(this.emailForm, 'body', '请填写邮件正文，比如：升级时间，注意事项。')
      // this.emailForm.recipient = account.Email
      this.emailFormVisible = true
    },
    closeAccount (account) {
      this.closeAccountvisible = true
      this.readyTodeleteAccount = account
    },
    async doCloseAccount () {
      try {
        this.$message({
          message: '发送中...',
          type: 'info'
        })
        await closeAccountApi({ AccountId: this.readyTodeleteAccount.Id }, { account_id: this.accountList[this.selectedAccount].account_id })
        this.$message({
          message: '成功',
          type: 'success'
        })
      } catch (e) {
        console.log(e)
        this.$message({
          message: '发送失败',
          type: 'error'
        })
      } finally {
        this.closeAccountvisible = false
      }
    },
    async sendMail () {
      try {
        this.$message({
          message: '发送中...',
          type: 'info'
        })
        await sendMailApi(this.emailForm, { account_id: this.accountList[this.selectedAccount].account_id })
        this.$message({
          message: '发送成功',
          type: 'success'
        })
      } catch (e) {
        console.log(e)
        this.$message({
          message: '发送失败',
          type: 'error'
        })
      } finally {
        this.emailFormVisible = false
      }
    }
  },
  mounted () {
    console.log('mounting...')
    this.$nextTick(() => {
      this.GetDeptList({}).then(res => {
        console.log(JSON.stringify(res))
        this.accountList = res.data.data.map(item => {
          item.account_id = item.account_id.toString(); return item
        })
        if (this.$store.state.d2admin.billgroup.selectedAccount === undefined) {
          console.log('selectedAccount is undefined')
          this.$store.commit('d2admin/billgroup/modify', 0)
        }
        this.selectedAccount = this.$store.state.d2admin.billgroup.selectedAccount
        this.$store.commit('d2admin/billgroup/account', this.accountList[this.selectedAccount])
        this.accountInOrgRequest({ account_id: this.accountList[this.selectedAccount].account_id })
      }).catch(err => {
        console.log(err)
      })
    })
  }
}
</script>

<style scoped>

</style>
