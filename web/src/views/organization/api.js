import { request } from '@/api/service'
export const orgUrlPrefix = '/api/aws/organization/'

export function GetAccountList (query) {
  return request({
    url: orgUrlPrefix + 'accounts/',
    method: 'get',
    params: query
  })
}

export function inviteAccountToOrg (obj, query) {
  return request({
    url: orgUrlPrefix + 'invite_account/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function createAccountToOrg (obj, query) {
  return request({
    url: orgUrlPrefix + 'create_account/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function GetPoliciesList (query) {
  return request({
    url: orgUrlPrefix + 'list_policies/',
    method: 'get',
    params: query
  })
}

export function GetPoliciesListForTarget (query) {
  return request({
    url: orgUrlPrefix + 'list_policies_for_target/',
    method: 'get',
    params: query
  })
}

export function attachPolicy (obj, query) {
  return request({
    url: orgUrlPrefix + 'attach_policy/',
    method: 'post',
    params: query,
    data: obj
  })
}
export function detachPolicy (obj, query) {
  return request({
    url: orgUrlPrefix + 'detach_policy/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function closeAccountApi (obj, query) {
  return request({
    url: orgUrlPrefix + 'close_account/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function sendMailApi (obj, query) {
  return request({
    url: orgUrlPrefix + 'send_notification/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function GetBillItems (query) {
  return request({
    url: '/api/aws/billing_group/account_monthly_bill/',
    method: 'get',
    params: query
  })
}

export function DownloadBill (query) {
  return request({
    url: '/api/aws/billing_group/download_monthly_bill/',
    method: 'get',
    params: query
  })
}
