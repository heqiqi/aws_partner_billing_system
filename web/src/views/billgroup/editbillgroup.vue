<template>
  <d2-container class="page">
    <p style="color: #909399" >{{ this.billgroup.Arn == 'create' ? '创建账单组' : '编辑账单组'}}</p>
    <hr>
    <el-tabs :tab-position="tabPosition" style="height: 90vh;">
      <el-tab-pane label="账单折扣管理">
        <el-card v-loading="!showCard" v-if="isCreatePlan">
          <el-form :model="ruleForm" :rules="rules" ref="ruleForm" label-width="100px" class="ruleForm">
            <el-form-item label="名称" prop="name">
              <el-input v-model="ruleForm.name" placeholder="账单组名称"></el-input>
            </el-form-item>
            <el-form-item label="描述" prop="description">
              <el-input v-model="ruleForm.description"  placeholder="账单组描述"></el-input>
            </el-form-item>
            <el-form-item label="创建新计划" prop="isCreatePlan">
              <el-switch v-model="ruleForm.isCreatePlan"></el-switch>
            </el-form-item>
            <el-form-item label="折扣比例" prop="discount" v-if="ruleForm.isCreatePlan">
              <el-input v-model="ruleForm.discount" placeholder="请填写数字：9折为90%" type="digit"></el-input>
            </el-form-item>
            <el-form-item label="折扣规则" prop="pricePlan" v-if="!ruleForm.isCreatePlan">
              <el-select v-model="ruleForm.checkedpricePlan" placeholder="请选择计划">
                <el-option v-for="pp in pricePlans" :label="pp.Arn"  :value="pp.Arn" :key="pp.Arn">{{pp.Name}}</el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="选择账号" prop="checkedAccount">
              <el-checkbox-group v-model="ruleForm.checkedAccount">
                <el-checkbox v-for="account in accounts" :label="account" :key="account" style="display: block; padding-top: 10px">{{account}}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="账单主账号" prop="checkedPrimaryAccount">
              <el-select v-model="ruleForm.checkedPrimaryAccount" placeholder="请选择主账号">
                <el-option v-for="pAccount in ruleForm.checkedAccount" :label="pAccount"  :value="pAccount" :key="pAccount"></el-option>
              </el-select>
            </el-form-item>
          </el-form>
          <el-button style="float: right; margin: 12px;" type="primary" @click="submitForm('ruleForm')">创建</el-button>
          <el-button style="float: right; margin: 12px;" @click="resetForm('ruleForm')">取消</el-button>
        </el-card>
        <el-card v-loading="!showCard" v-if="!isCreatePlan">
          <el-form :model="billgroup" :rules="editRules" ref="editForm" label-width="100px" class="ruleForm">
            <el-form-item label="名称" prop="Name" >
              <el-input v-model="billgroup.Name" disabled placeholder="账单组名称"></el-input>
            </el-form-item>
            <el-form-item label="描述" prop="Description" >
              <el-input v-model="billgroup.Description" disabled  placeholder="账单组描述"></el-input>
            </el-form-item>
            <el-form-item label="账单主账户" prop="PrimaryAccountId" >
              <el-input v-model="billgroup.PrimaryAccountId" disabled  placeholder="主账号"></el-input>
            </el-form-item>
            <el-form-item label="包含账户" prop="Accounts" >
              <el-table
                :data="accounts"
                stripe
                size="medium"
                :show-header="false"
                border
                style="width: 90%">
                <el-table-column
                  prop="AccountName"
                  width="180">
                </el-table-column>
                <el-table-column
                  prop="AccountId"
                  width="180">
                </el-table-column>
                <el-table-column
                  prop="AccountEmail"
                  width="180">
                </el-table-column>
                <el-table-column
                  align="center">
                  width="60">
                  <template slot-scope="scope">
                    <el-button
                      @click="unassociateAcc(scope.row)"
                      type="text"
                      size="small">
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>
            <el-form-item label="选择账号">
              <el-checkbox-group v-model="checkedUnassociateAccount" @change="selectedNewAccount()">
                <el-checkbox v-for="acc in unassociateAccounts" :label="acc" :key="acc" style="display: block; padding-top: 10px">{{acc}}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="折扣规则" prop="pricePlan">
              <el-select style="width: 40%" v-model="billgroup.ComputationPreference.PricingPlanArn" placeholder="请选择计划">
                <el-option v-for="pp in pricePlans" :label="pp.Name"  :value="pp.Arn" :key="pp.Arn">{{pp.Name}}</el-option>
              </el-select>
<!--                        <el-button type="primary" round plain style="margin-left: 2vw" @click="showPlanRule()">详情</el-button>-->
              <el-button type="primary" round plain style="margin-left: 2vw" @click="showPlanForm('pPlanForm')">新增</el-button>
            </el-form-item>
          </el-form>
          <el-button style="float: right; margin: 12px;" type="primary" @click="submitChangeForm()">提交</el-button>
          <el-button style="float: right; margin: 12px;" @click="resetForm('ruleForm')">取消</el-button>
        </el-card>
      </el-tab-pane>
      <el-tab-pane v-loading="!showCard" label="附加费用管理">
        <el-card style="height: 80vh;"  v-loading="!showCard">
          <el-table
            :data="customLineList"
            stripe
            border
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
              label="所属账单组"
              width="120">
              <template slot-scope="scope">
                {{scope.row.BillingGroupName}}
              </template>
            </el-table-column>
            <el-table-column
              label="每月绝对费用"
              width="60">
              <template slot-scope="scope">
              {{scope.row.ChargeDetails.Flat !== undefined ? scope.row.ChargeDetails.Flat.ChargeValue + ' USD' : '-'}}
              </template>
            </el-table-column>
            <el-table-column
              label="每月相对费用"
              width="60">
              <template slot-scope="scope">
              {{scope.row.ChargeDetails.Percentage !== undefined ? scope.row.ChargeDetails.Percentage.PercentageValue+'%' : '-' }}
              </template>
            </el-table-column>
            <el-table-column
              label="操作"
              width="120">
              <template slot-scope="scope">
                <el-button
                  @click.native.prevent="editCustomLine(scope.row)"
                  type="text"
                  size="small">
                  编辑
                </el-button>
                <el-button
                  @click="deleteCustomLine(scope.row)"
                  type="text"
                  size="small">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <br>
          <el-button style="float: right; margin-right: 5vw" type="primary" @click="showCustomItemCreator=true" size="small"  icon="el-icon-plus">新增</el-button>
        </el-card>
      </el-tab-pane>
    </el-tabs>

<!--dialog billing plan-->
    <el-dialog title="创建折扣规则" :visible.sync="dialogFormVisible">
      <el-form :model="newPlan" :rules="newPlanRules" v-loading="isCreatingPlan">
        <el-form-item label="规则名称"  prop="name" >
          <el-input v-model="newPlan.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="折扣比例"  prop="discount" >
          <el-input v-model="newPlan.discount" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="confirmCreatePlan">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog title="创建附加费用" :visible.sync="showCustomItemCreator" >
      <el-form :model="customLineForm" :rules="newCustomLineRules" style="width: 85%;" v-loading="!showCard">
        <el-form-item label="名称"  prop="Name" :label-width="formLabelWidth">
          <el-input v-model="customLineForm.Name" ></el-input>
        </el-form-item>
        <el-form-item label="描述"   prop="Description" :label-width="formLabelWidth">
          <el-input v-model="customLineForm.Description" ></el-input>
        </el-form-item>
        <el-form-item label="账单组" :label-width="formLabelWidth" prop="BillingGroupArn">
          <el-select v-model="customLineForm.BillingGroupArn" placeholder="请选择账单组">
            <el-option v-for="bg in this.$store.state.d2admin.billgroup.billingGroupList" :label="bg.Name"  :value="bg.Arn" :key="bg.Arn">{{bg.Name}}</el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="计费方式" :label-width="formLabelWidth" prop="isFlat">
          <el-select v-model="customLineForm.isFlat" placeholder="请选择账单组">
            <el-option label="固定金额" value=true></el-option>
            <el-option label="用量百分比" value=false></el-option>
          </el-select>
        </el-form-item>
        <el-row>
          <el-col :span="12">
            <div class="grid-content bg-purple">
              <el-form-item label="CREDIT" prop="Credit" :label-width="formLabelWidth">
                <el-input v-model="customLineForm.Credit" type="number"></el-input>
              </el-form-item>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="grid-content bg-purple-light">
              <el-form-item label="FEE" label-position="top" prop="Fee" :label-width="formLabelWidth">
                <el-input v-model="customLineForm.Fee" type="number"></el-input>
              </el-form-item>
            </div>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCustomItemCreator = false">取 消</el-button>
        <el-button type="primary" @click="doCreateOperation">确 定</el-button>
      </div>
    </el-dialog>
<!--    <PriceRuleInfo-->
<!--      :visible.sync="pRuleDetailsVisible"-->
<!--      :arn="priceRuleArn"-->
<!--      />-->
  </d2-container>
</template>

<script>
import {
  createBillingGroup, CreateCustomLineItem,
  CreatePricingPlanRule, DeleteCustomLineItem,
  ListAccountAssociations, ListCustomLineItems,
  ListPricingPlans, UpdateBillingGroup
} from '@/views/billgroup/api'
import axios from 'axios'

export default {
  name: 'bill_group_form',
  // components: {
  //   PriceRuleInfo
  // },
  data () {
    const regex = /^[a-zA-Z0-9]+$/
    const validateName = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入名称'))
      } else if (regex.test(value) && value.length > 3) {
        console.log(' match regex')
        callback()
      } else {
        callback(new Error('名称不能有特殊符号和空格，长度大于3，小于128'))
      }
    }
    return {
      tabPosition: 'left',
      billgroup: { Arn: 'create' },
      showCard: false,
      isCreatePlan: true,
      customLineList: [],
      ca: [],
      timer: null,
      accounts: [],
      oldAccountsRaw: [],
      pricePlans: [],
      dialogFormVisible: false,
      isCreatingPlan: false,
      newPlan: {
        name: '',
        discount: ''
      },
      ruleForm: {
        name: '',
        description: '',
        isCreatePlan: true,
        discount: '',
        pricePlan: '',
        checkedAccount: [],
        checkedPrimaryAccount: '',
        checkedpricePlan: ''
      },
      editRules: {},
      rules: {
        name: [
          { validator: validateName, trigger: 'blur', required: true }
        ],
        description: [
          {
            required: false,
            trigger: 'blur'
          }
        ],
        discount: [
          {
            pattern: /^(?:1\d{2}|200|\d{1,2})$/,
            message: '请填写200以内数字：9折为90%，故填写90',
            trigger: 'blur'
          }
        ],
        checkedAccount: [
          {
            type: 'array',
            required: true,
            message: '请至少选择一个账号',
            trigger: 'change'
          }
        ],
        checkedPrimaryAccount: [
          {
            required: true,
            message: '请选择主账号',
            trigger: 'change'
          }
        ]
      },
      newPlanRules: {
        name: [
          { validator: validateName, trigger: 'blur', required: true }
        ],
        discount: [
          {
            pattern: /^(?:1\d{2}|200|\d{1,2})$/,
            message: '请填写200以内数字：9折为90%，故填写90',
            trigger: 'blur'
          }
        ]
      },
      newCustomLineRules: {
        Name: [
          { validator: validateName, trigger: 'blur', required: true }
        ],
        Description: [
          {
            required: true,
            message: '填写描述',
            trigger: 'blur'
          }
        ],
        BillingGroupArn: [
          { required: true, message: '请选择账单组', trigger: 'change' }
        ],
        isFlat: [
          { required: true, message: '请选择计费方式', trigger: 'change' }
        ],
        Credit: [
          {
            pattern: /^(10000|[1-9]\d{0,3})$/,
            message: '请填写10000以内数字',
            trigger: 'blur'
          }
        ],
        Fee: [
          {
            pattern: /^(10000|[1-9]\d{0,3})$/,
            message: '请填写10000以内数字',
            trigger: 'blur'
          }
        ]
      },
      showCustomItemCreator: false,
      formLabelWidth: '100px',
      customLineForm: { BillingGroupArn: '', Credit: '', Fee: '' },
      disableInput: true,
      unassociateAccounts: [],
      unassociateAccountsRaw: [],
      checkedUnassociateAccount: [],
      pRuleDetailsVisible: false,
      priceRuleArn: ''
    }
  },
  methods: {
    start () {
      if (this.$store.state.d2admin.billgroup.selectedAccount === undefined) {
        this.$message({
          type: 'warning',
          message: '请先选择账号'
        })
        this.$router.go(-1)
        return
      }
      this.timer = setInterval(this.valChange, 1000)
    },
    valChange () {
      console.log(JSON.stringify(this.checkedUnassociateAccount))
    },
    createBillGroupWithMsg (f) {
      this.$message({
        type: 'warning',
        message: '创建中...'
      })
      this.showCard = false
      console.log('submit!', f)
      createBillingGroup(f, { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id }).then(resp => {
        console.log('createBillingGroup: ', resp)
        this.$message({
          type: 'success',
          message: '创建成功'
        })
        this.$router.go(-1)
      }).catch(err => {
        console.log('createBillingGroup error: ', err)
        this.$message({
          type: 'error',
          message: '创建失败'
        })
        this.showCard = true
      })
    },
    prepareData () {
      const billApis = [ListAccountAssociations(this.isCreatePlan ? { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id } : { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id, arn: this.billgroup.Arn }),
        ListPricingPlans({ account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id }),
        ListAccountAssociations({ account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
      ]
      axios.all(billApis)
        .then(axios.spread((accounts, pPlans, unassociateAccounts) => {
          // console.log('----- 所有请求完成 -----')
          console.log('accounts: ', JSON.stringify(accounts))
          console.log('pPlans: ', JSON.stringify(pPlans))
          // {
          //   "AccountId": "331059269292",
          //   "AccountName": "qihen-billconductor-created",
          //   "AccountEmail": "qihen+billconductorCreated@amazon.com"
          // }
          if (this.isCreatePlan) {
            this.accounts = accounts.data.map((item) => {
              return item.AccountId
            })
          } else {
            this.accounts = accounts.data.map((item) => {
              return item
            })
            this.oldAccountsRaw = accounts.data
            this.unassociateAccounts = unassociateAccounts.data.map((item) => {
              return item.AccountId
            })
            this.unassociateAccountsRaw = unassociateAccounts.data.concat(accounts.data)
            console.log('unassociateAccounts:' + JSON.stringify(this.unassociateAccounts))
          }
          this.pricePlans = pPlans.data
          this.showCard = true
        }))
        .catch(function (error) {
          console.log(error)
        })
    },
    submitForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.$confirm('此操作将创建新的账单组, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            this.createBillGroupWithMsg(this.ruleForm)
          }).catch(() => {
            this.$message({
              type: 'info',
              message: '已取消创建'
            })
          })
        } else {
          console.log('error')
          return false
        }
      })
    },
    resetForm (formName) {
      // 返回上一页
      this.$router.go(-1)
    },
    showPlanForm (f) {
      this.dialogFormVisible = true
    },
    showPlanRule () {
      this.pRuleDetailsVisible = true
    },
    confirmCreatePlan (f) {
      this.$message({
        type: 'warning',
        message: '创建中...'
      })
      this.isCreatingPlan = true
      CreatePricingPlanRule(this.newPlan, { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
        .then(resp => {
          this.$message({
            type: 'success',
            message: '创建成功'
          })
          console.log('CreatePricingPlanRule: ', resp)
          this.pricePlans.unshift(resp.data)
          this.billgroup.ComputationPreference.PricingPlanArn = resp.data.Arn
          this.isCreatingPlan = false
          this.dialogFormVisible = false
        }).catch(() => {
          this.isCreatingPlan = false
          this.$message({
            type: 'danger',
            message: '创建失败'
          })
        })
    },
    submitChangeForm () {
      this.$confirm('此操作将更新该账单组的价格计划, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message({
          type: 'warning',
          message: '更新中...'
        })
        this.showCard = false
        this.billgroup.Accounts = this.accounts
        this.billgroup.OldAccounts = this.oldAccountsRaw
        UpdateBillingGroup(this.billgroup, { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
          .then(res => {
            this.$message({
              type: 'success',
              message: '更新成功'
            })
            console.log('UpdateBillingGroup: ', res)
            this.showCard = true
          })
          .catch(() => {
            this.$message({
              type: 'danger',
              message: '更新失败'
            })
            throw new Error('更新失败')
          })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消'
        })
        this.showCard = true
      })
    },
    getCustomLine (query) {
      ListCustomLineItems(query).then(resp => {
        console.log('resp ListCustomLineItems', JSON.stringify(resp))
        const final = resp.data.map(item1 => {
          const same = this.$store.state.d2admin.billgroup.billingGroupList.find(item2 => item2.Arn === item1.BillingGroupArn)
          if (same) {
            item1.BillingGroupName = same.Name
          }
          if (item1.ChargeDetails.Type === 'CREDIT') {
            if (item1.ChargeDetails.Flat !== undefined) {
              item1.ChargeDetails.Flat.ChargeValue = -item1.ChargeDetails.Flat.ChargeValue
            }
            if (item1.ChargeDetails.Percentage !== undefined) {
              item1.ChargeDetails.Percentage.PercentageValue = -item1.ChargeDetails.Percentage.PercentageValue
            }
          }
          return item1
        })
        // console.log('final ListCustomLineItems', JSON.stringify(final))
        this.customLineList = final
        this.showCard = true
      })
    },
    deleteCustomLine (row) {
      console.log('row', JSON.stringify(row))
      this.$confirm('此操作将永久删除, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message({
          type: 'warning',
          message: '删除中...'
        })
        this.showCard = false
        DeleteCustomLineItem({ Arn: row.Arn, ChargeDetails: row.ChargeDetails, BillingGroupArn: row.BillingGroupArn }, { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
          .then(() => {
            this.$message({
              type: 'success',
              message: '删除成功'
            })
            this.getCustomLine({ account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
          })
          .catch(err1 => {
            this.$message({
              type: 'error',
              message: '删除失败'
            })
            this.showCard = true
          })
      }).catch(err => {
        console.log(err)
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
      this.showCard = true
    },
    editCustomLine (row) {
      this.$message({
        type: 'success',
        message: '紧张开发中...'
      })
    },
    async doCreateOperation () {
      this.showCard = false
      this.$message({
        type: 'info',
        message: '创建中...'
      })
      try {
        const res = await CreateCustomLineItem(this.customLineForm, { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
        console.log(res)
        this.$message({
          type: 'success',
          message: '创建完成'
        })
        this.showCustomItemCreator = false
        this.getCustomLine({ account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
      } catch (e) {
        console.log(e)
      } finally {
        this.showCard = true
      }
    },
    unassociateAcc (account) {
      console.log(JSON.stringify(account))
      if (account.AccountId === this.billgroup.PrimaryAccountId) {
        this.$message({
          type: 'warning',
          message: '主账号不能取消关联'
        })
        return
      }
      this.accounts = this.accounts.filter(obj => {
        return obj.AccountId !== account.AccountId
      })
      this.unassociateAccounts.push(account.AccountId)
    },
    selectedNewAccount () {
      console.log('changed', this.checkedUnassociateAccount)
      const accId = this.checkedUnassociateAccount[0]
      const newAccount = this.unassociateAccountsRaw.filter(account => {
        return account.AccountId === accId
      })
      console.log('newAccount', JSON.stringify(newAccount), JSON.stringify(this.unassociateAccountsRaw))
      this.accounts.push(newAccount[0])
      this.unassociateAccounts = this.unassociateAccounts.filter(account => {
        return account !== accId
      })
      this.checkedUnassociateAccount = []
    }
  },
  mounted () {
    console.log('mounting...', this.isCreatePlan)
    this.start()
    this.prepareData()
    this.getCustomLine({ account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
  },
  beforeDestroy () {
    clearInterval(this.timer)
  },
  watch: {
  },
  created () {
    if (this.$route.params.obj !== undefined) {
      this.billgroup = this.$route.params.obj
      this.isCreatePlan = (this.billgroup.Arn === 'create')
    }
  }
}
</script>

<style scoped>
hr {
  border: none;
  height: 1px;
  background-color: #CCCCCC;
}

.circle-chart {
  height: 33vh;
  display: flex;
  justify-content: center;
  align-content: center;
}

.centered-span {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
/*水平排列 */
.creditFee {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.creditFee {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50%;
}
.block {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 10px;
}
</style>
