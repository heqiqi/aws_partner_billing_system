<template>
  <div>
    <el-dialog v-bind="$attrs" v-on="$listeners" @open="onOpen" @close="onClose" title="Price Rule Details" :visible.sync="visible">
      <el-row :gutter="15">
        <el-form ref="elForm" :model="formData" :rules="rules" size="medium" label-width="100px">
          <el-col :span="13">
            <el-form-item label="Scope" prop="scope">
              <el-input disable v-model="formData.scope" placeholder="请输入Scope" prefix-icon='el-icon-monitor'
                        :style="{width: '100%'}"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="13">
            <el-form-item label="Rate" prop="rate">
              <el-input v-model="formData.rate" placeholder="请输入Rate" :style="{width: '100%'}"></el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
    </el-dialog>
  </div>
</template>

<script>
import { CreateCustomLineItem, GetPriceRuleDetails } from '@/views/billgroup/api'

export default {
  name: 'PriceRuleInfo',
  inheritAttrs: false,
  components: {},
  props: {
    // visible: {
    //   type: Boolean,
    //   default: false
    // }
  },
  data () {
    return {
      visible: false,
      formData: {
        scope: 'Global',
        rate: '0%'
      },
      rules: {
        scope: [{
          required: true,
          message: '请输入Scope',
          trigger: 'blur'
        }],
        rate: [{
          required: true,
          message: '请输入Rate',
          trigger: 'blur'
        }],
      },
    }
  },
  computed: {},
  created () {
  },
  mounted () {
  },
  methods: {
    async showDialog (arn) {
      console.log(arn)
      this.visible = true
      try {
        const res = await GetPriceRuleDetails({ Arn: arn }, { account_id: this.$store.state.d2admin.billgroup.accountDetails.account_id })
        console.log(JSON.stringify(res))
        this.formData.scope = res.data.PricingRules[0].Scope
        this.formData.rate = res.data.PricingRules[0].Type + ' - ' + res.data.PricingRules[0].ModifierPercentage + ' %'
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    onOpen () {
      console.log('open priceRule Dialog')
    },
    onClose () {
      console.log('onClose priceRule Dialog')
      this.$refs['elForm'].resetFields()
    },
    close () {
      console.log('close dialog')
      this.$emit('update:visible', false)
    }
  },
  watch: {
    arn (newVal, oldVal) {
      console.log(`新值：${newVal}`)
      console.log(`旧值：${oldVal}`)
    }
  }
}
</script>

<style scoped>

</style>
