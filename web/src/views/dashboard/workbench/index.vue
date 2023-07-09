<template>
  <d2-container>
    <el-tabs type="border-card" v-model="currentTab" v-if="showTabList">
      <el-tab-pane v-for="(tab,index) in tabList" :key="index" :label="tab.account_id">
        <iframe
          width="100%"
          height="720"
          v-bind:src=tab.dashboard_url>
        </iframe>
      </el-tab-pane>
    </el-tabs>
    <el-empty style="position: absolute;padding: 0px 0!important;width: 100%;" v-if="!showTabList" description="未查到任何账单组信息,请在“系统管理”-->“账号管理”下设置payer账号。"></el-empty>

  </d2-container>
</template>
<script>
import allComps from './components'
import initData from './init.js'
import { request } from '@/api/service'

export default {
  components: {
  },
  data () {
    return {
      customizing: false,
      allComps: allComps,
      selectLayout: [],
      defaultLayout: initData,
      layout: [],
      colNum: 48,
      minimize: false,
      pxData: {},
      isLoading: false,
      currentTab: '0',
      tabList: [],
      showTabList: true
    }
  },
  created () {
  },
  computed: {
    allCompsList () {
      var allCompsList = []
      for (var key in this.allComps) {
        allCompsList.push({
          key: key,
          sort: allComps[key].sort,
          title: allComps[key].title,
          icon: allComps[key].icon,
          height: allComps[key].height,
          width: allComps[key].width,
          config: allComps[key].config || {},
          isResizable: allComps[key].isResizable || null,
          description: allComps[key].description
        })
      }
      allCompsList.sort(function (a, b) {
        return (a.sort || 0) - (b.sort || 0)
      })
      return allCompsList
    },
    myCompsList () {
      return this.allCompsList
    },
    nowCompsList () {
      return this.allCompsList
    }
  },
  methods: {
    GetDeptList (query) {
      return request({
        url: '/api/system/menu/dashboard_url/',
        method: 'get',
        params: query
      })
    }
  },
  mounted () {
    this.GetDeptList({}).then(res => {
      console.log(JSON.stringify(res))
      this.showTabList = (res.data.data.length > 0)
      this.tabList = res.data.data.map(item => {
        item.account_id = item.account_id.toString(); return item
      })
      this.isLoading = false
    })
  }
}
</script>
<style scoped lang="scss">
::v-deep .d2-container-full__body {
  padding: 0!important;
}

.widgetsListItem {
  width: 168px;
  height: 75px;
  border-radius: 4px 4px 4px 4px;
  font-size: 16px;
  font-family: Microsoft YaHei-Bold, Microsoft YaHei;
  font-weight: bold;
  color: #ffffff;
  text-align: center;
  margin-left: 7px;
  line-height: 75px;
  margin-bottom: 10px;
  position: initial;
}

.widgetsListBox {
  display: flex;
  flex-wrap: wrap;
  margin-top: 20px;
  z-index: 999999;
}

.component-header {
  background-color: #FFFFFF;
  position: sticky;
  top: -20px;
  z-index: 99;

  .set-btn-class {
    float: right;
    z-index: 99;
  }

  .all-component-class {
    clear: right;

    .widgets-list {
      display: flex;
      justify-content: space-between;
      overflow-x: scroll;
      padding-bottom: 10px;

      .widgets-list-item {
        margin-right: 10px;
      }

      .widgets-list-item:last-child {
        margin-right: 0px;
      }
    }
  }
}

.widgets-wrapper-bg {
  background: rgba(180, 180, 180, .2);
  min-height: 500px;
}

.widgets-wrapper .sortable-ghost {
  opacity: 0.5;
}

.set-component-bg {
  //background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(0, 0, 0, .5);
}

.customize-overlay {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 5px;
  left: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.5);
  cursor: move;
}

.customize-overlay label {
  background: #409EFF;
  color: #fff;
  height: 40px;
  padding: 0 30px;
  border-radius: 40px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: move;
}

.customize-overlay label i {
  margin-right: 15px;
  font-size: 24px;
}

.customize-overlay .close {
  position: absolute;
  top: 15px;
  right: 15px;
}

</style>
