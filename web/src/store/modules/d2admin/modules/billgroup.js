export default {
  namespaced: true,
  state: {
    // 用户信息
    selectedAccount: undefined,
    accountDetails: {},
    billingGroupList: []
  },
  mutations: {
    modify (state, msg) {
      state.selectedAccount = msg
    },
    account (state, msg) {
      state.accountDetails = msg
    },
    updateBillingGroup (state, msg) {
      state.billingGroupList = msg
    }
  }
}
