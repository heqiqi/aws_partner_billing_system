<template>
  <el-dialog title="折扣详情" :visible.sync="visible" v-loading="!isShow">
    <el-table :data="gridData">
      <el-table-column property="date" label="日期" width="150"></el-table-column>
      <el-table-column property="name" label="姓名" width="200"></el-table-column>
      <el-table-column property="address" label="地址"></el-table-column>
    </el-table>
  </el-dialog>
</template>

<script>
export default {
  name: 'PriceRuleInfo',
  components: {},
  props: {
    arn: {
      type: String,
      default: ''
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      gridData: [{
        date: '2016-05-02',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1518 弄'
      }],
      pRule: {},
      isShow: false
    }
  },
  watch: {
    arn (newVal, oldVal) {
      console.log(`新值：${newVal}`)
      console.log(`旧值：${oldVal}`)
      console.log('hellow  world')
    }
  }
}
</script>

<style scoped>

</style>
