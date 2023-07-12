<template>
  <d2-container>
    <div style="color: #909399">
      费用总览
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
    <el-card v-loading="!showEchart" >
      <div  class="circle-chart">
      <div id="myChart" style="height: 100%; width: 50%;"></div>
        <div class="info-block-container" v-if="!emptyContent">
          <div class="info-block">
            <div class="fee-type-style">总收入：</div>
            <h2>{{totalCharged | currencyFormat}}</h2>
          </div>
          <div class="info-block">
            <div class="fee-type-style">总支出：</div>
            <h2>{{totalAwsCost | currencyFormat}}</h2>
          </div>
          <div class="info-block">
            <div class="fee-type-style">总利润：</div>
            <h2>{{totalMargin | currencyFormat}}</h2>
          </div>
          <div class="info-block">
            <div class="fee-type-style">监控账户数：</div>
            <h2>{{countAccount}}</h2>
          </div>
        </div>
      <el-empty style="position: absolute;padding: 0px 0!important;width: 100%;" v-if="emptyContent" description="未查到任何账单组信息,请点击右下按钮“新增”。"></el-empty>
      </div>
    </el-card>
    <br>
    <el-card v-loading="!showEchart">
<!--      <div style="color: #909399">-->
<!--        账单折扣组-->
<!--      </div>-->
<!--      <hr>-->
      <div slot="header" class="clearfix">
        <span>账单折扣组</span>
      </div>
      <el-table
        :data="billGroup"
        stripe
        border
        style="width: 100%">
        <el-table-column
          prop="Name"
          label="名称"
          width="180">
        </el-table-column>
        <el-table-column
          prop="Size"
          label="账号数量"
          width="120">
        </el-table-column>
        <el-table-column
          prop="AWSCost"
          label="消耗费用"
          width="180">
          <template slot-scope="scope">
            {{scope.row.AWSCost |currencyFormat}}
          </template>
        </el-table-column>
        <el-table-column
          prop="ProformaCost"
          label="应收费用"
          width="180">
          <template slot-scope="scope">
            {{scope.row.ProformaCost |currencyFormat}}
          </template>
        </el-table-column>
        <el-table-column
          prop="Margin"
          label="利润"
          width="180">
          <template slot-scope="scope">
            {{scope.row.Margin |currencyFormat}}
          </template>
        </el-table-column>
        <el-table-column
          prop="PrimaryAccountId"
          label="主账号">
        </el-table-column>
        <el-table-column
          fixed="right"
          label="操作"
          width="120">
          <template slot-scope="scope">
            <el-button
              @click.native.prevent="editRow(scope.row)"
              type="text"
              size="small">
              编辑
            </el-button>
            <el-button
              @click="deleteRow(scope.row)"
              type="text"
              size="small">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <br>
      <div>
        <el-button style="float: right; margin-right: 5vw; margin-bottom: 16px;" type="primary" @click="createGillGroup()" size="small"  icon="el-icon-plus">新增  </el-button>
      </div>
    </el-card>
    <br>

    <el-dialog
      title="提示"
      :visible.sync="deleteDialogVisible"
      width="30%"
      center>
      <span class="centered-span">确定删除？</span>
      <span slot="footer" class="dialog-footer">
    <el-button @click="deleteDialogVisible = false">取 消</el-button>
    <el-button type="primary" @click="centerDialogVisible = false">确 定</el-button>
      </span>
    </el-dialog>

  </d2-container>
</template>

<script>

import {
  GetList,
  GetBillGroupList,
  DeleteBillGroup,
  inviteAccountToOrg,
  createAccountToOrg
} from './api'
import axios from 'axios'
import { request } from '@/api/service' // 查询添加修改删除的http请求接口
export default {
  name: 'bill_group',
  props: {
    dataList: Array,
    type: Number
  },
  data () {
    return {
      selectedAccount: 0,
      accountList: [],
      data: [],
      showEchart: false,
      billGroupCostReport: [],
      billGroup: [],
      pieData: [],
      legendData: ['aws cost'],
      deleteDialogVisible: false,
      myChart: null,
      emptyContent: false,
      totalCharged: 0,
      totalAwsCost: 0,
      totalMargin: 0,
      countAccount: 0,
      accountGroup: [],
      showOrgAccountCreator: false,
      isCreateNewAccount: false,
      showDialog: true,
      orgAccountForm: {},
      formLabelWidth: '120px',
      accOptions: [{
        value: 'EMAIL',
        label: '注册邮箱'
      }, {
        value: 'ACCOUNT',
        label: 'AWS ID'
      }]
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
    createGillGroup () {
      console.log('createGillGroup')
      this.$router.push({
        name: 'editBillGroup',
        params: {
          obj: { Arn: 'create' }
        }
      })
    },
    deleteRow (row) {
      console.log(JSON.stringify(row))
      this.$confirm('此操作将永久删除该账单组, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message({
          type: 'warning',
          message: '删除中...'
        })
        this.showEchart = false
        DeleteBillGroup({ arn: row.Arn }, { account_id: this.accountList[this.selectedAccount].account_id })
          .then(resp => {
            this.billGroupRequest({ account_id: this.accountList[this.selectedAccount].account_id })
            this.$message({
              type: 'success',
              message: '删除成功'
            })
          })
          .catch(() => {
            this.billGroupRequest({ account_id: this.accountList[this.selectedAccount].account_id })
            this.$message({
              type: 'error',
              message: '删除失败'
            })
          })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    editRow (row) {
      console.log('editRow', JSON.stringify(row))
      this.$router.push({
        name: 'editBillGroup',
        params: {
          obj: row
        }
      })
    },
    mergeArraysByObjectArn (arr1, arr2) {
      const mergedArray = [...arr1]
      arr2.forEach(obj2 => {
        const foundIndex = mergedArray.findIndex(obj1 => obj1.Arn === obj2.Arn)
        if (foundIndex !== -1) {
          // 对象已存在，进行合并
          mergedArray[foundIndex] = { ...mergedArray[foundIndex], ...obj2 }
        } else {
          // 对象不存在，直接添加到合并数组
          mergedArray.push(obj2)
        }
      })
      return mergedArray
    },
    processInfoFromBillingGroup (bg) {
      this.totalCharged = 0
      this.totalAwsCost = 0
      this.totalMargin = 0
      this.countAccount = 0
      bg.map(item => {
        this.totalCharged += Number(item.ProformaCost)
        this.totalAwsCost += Number(item.AWSCost)
        this.totalMargin += Number(item.Margin)
        this.countAccount += Number(item.Size)
      })
    },
    billGroupRequest (query) {
      const billApis = [GetList(query), GetBillGroupList(query)]
      axios.all(billApis)
        .then(axios.spread((costReports, billGroup) => {
          // console.log('----- 所有请求完成 -----')
          // console.log('costReports: ', JSON.stringify(costReports))
          // console.log('billGroup: ', JSON.stringify(billGroup))
          this.billGroupCostReport = costReports.data
          this.billGroup = this.mergeArraysByObjectArn(this.billGroupCostReport, billGroup.data)
          this.processInfoFromBillingGroup(this.billGroup)
          // test
          // this.billGroup = []
          // test end
          this.$store.commit('d2admin/billgroup/updateBillingGroup', this.billGroup)
          console.log('billGroup: ', JSON.stringify(this.billGroup))
          this.pieData = this.billGroup.map(item => {
            return {
              value: Number(item.AWSCost).toFixed(2),
              name: `账单组: ${item.Name}`
            }
          })
          this.legendData = this.billGroup.map(item => {
            return `账单组: ${item.Name}`
          })
          console.log(this.legendData)
          if (this.billGroup.length === 0) {
            this.emptyContent = true
          } else {
            this.emptyContent = false
            this.drawLine()
          }
          this.showEchart = true
        }))
        .catch(function (error) {
          console.log(error)
        })
    },
    drawLine () {
      console.log('drawLine')
      this.myChart.setOption({
        tooltip: {
          trigger: 'item',
          // eslint-disable-next-line no-template-curly-in-string
          formatter: '{b}:<br/>费用：${c}<br/>占比：{d}%',
          textStyle: {
            fontSize: '16'
          }
        }, // 提示文本的显示
        title: {
          text: '{b|费用构成}',
          textStyle: {
            rich: {
              b: {
                fontSize: '16'
              }
            }
          },
          left: 'center',
          top: 'center'
        },
        legend: {
          orient: 'vertical',
          x: 'left',
          data: this.legendData
        }, // 用例
        series: [
          {
            name: '账单组费用',
            type: 'pie',
            radius: ['70%', '95%'], // 半径，比例模式['50%', '70%']
            avoidLabelOverlap: false,
            center: ['50%', '50%'], // 位置：左右，上下；13+radius,20+radius
            label: {
              normal: {
                show: false,
                position: 'center',
                formatter: '{a}分析' // 处理hover环形图显示的文本
                // color:'blue' // 中间显示文字的颜色
              }, // 固定文本hover效果，普通状态环形圈中间文本（各个模块文本保持一致时使用）
              emphasis: {
                show: false,
                textStyle: {
                  fontSize: '12',
                  fontWeight: 'bold'
                }
              } // 不固定文本hover效果，环形圈中间文本 强调状态（各个模块文本不同时使用）
            },
            data: this.pieData // 数据来源
          }
        ]
      })
    },
    // async accountInOrgRequest (query) {
    //   const account = await GetAccountList(query)
    //   console.log(JSON.stringify(account))
    //   this.accountGroup = account.data
    // },
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
        // await this.accountInOrgRequest({ account_id: this.accountList[this.selectedAccount].account_id })
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
    }
  },
  watch: {
    selectedAccount (newValue, oldValue) {
      console.log('selectedAccount', newValue, 'oldValue', oldValue, ' ', JSON.stringify(this.$store.state.d2admin.billgroup.accountDetails), ' test ', this.$store.state.d2admin.billgroup.selectedAccount)
      if (newValue !== oldValue) {
        this.showEchart = false
        this.accountGroup = []
        // this.accountInOrgRequest({ account_id: this.accountList[this.selectedAccount].account_id })
        this.billGroupRequest({ account_id: this.accountList[newValue].account_id })
        this.$store.commit('d2admin/billgroup/modify', newValue)
        this.$store.commit('d2admin/billgroup/account', this.accountList[newValue])
      }
    }
  },
  mounted () {
    console.log('mounting...')
    this.myChart = null
    this.$nextTick(() => {
      this.myChart = this.$echarts.init(document.getElementById('myChart'))
      this.GetDeptList({}).then(res => {
        console.log(JSON.stringify(res))
        this.accountList = res.data.data.map(item => {
          item.account_id = item.account_id.toString(); return item
        })
        if (this.$store.state.d2admin.billgroup.selectedAccount === undefined) {
          this.$store.commit('d2admin/billgroup/modify', 0)
        }
        this.selectedAccount = this.$store.state.d2admin.billgroup.selectedAccount
        this.$store.commit('d2admin/billgroup/account', this.accountList[this.selectedAccount])
        // this.accountInOrgRequest({ account_id: this.accountList[this.selectedAccount].account_id })
        this.billGroupRequest({ account_id: this.accountList[this.selectedAccount].account_id })
      }).catch(err => {
        console.log(err)
      })
    })
  }
}
</script>

<style scoped>
 hr {
   border: none;
   height: 1px;
   background-color:#CCCCCC;
 }
 .circle-chart {
   height:38vh;
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
 .info-block-container {
   display: flex;
   flex-wrap: wrap;
   justify-content: space-around;
   width: 50%;
   height: 100%;
 }

 .info-block {
   width: 45%;
   height: 45%;
   margin: 2%;
   background-color: #fafafa;
   display: flex;
   flex-direction: column;
   align-items: center;
   justify-content: center;
 }
 .fee-type-style {
   font-size: 16px;
   color: #909399;
   margin-bottom: 8px;
 }
</style>
