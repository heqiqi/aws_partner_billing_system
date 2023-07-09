import { request } from '@/api/service'
export const urlPrefix = '/api/aws/billing_group/'
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

export function GetPriceRuleDetails (obj, query) {
  return request({
    url: urlPrefix + 'pricing_rule_details_by_pricing_plan/',
    method: 'post',
    params: query,
    data: obj
  })
}
export function GetBillGroupList (query) {
  return request({
    url: urlPrefix + 'bill_group_remote/',
    method: 'get',
    params: query
  })
}

export function GetList (query) {
  return request({
    url: urlPrefix + 'list_billing_group_cost_reports/',
    method: 'get',
    params: query
  })
}

export function ListCustomLineItems (query) {
  return request({
    url: urlPrefix + 'list_custom_line_items/',
    method: 'get',
    params: query
  })
}

export function CreateCustomLineItem (obj, query) {
  return request({
    url: urlPrefix + 'create_custom_line_item/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function DeleteCustomLineItem (obj, query) {
  return request({
    url: urlPrefix + 'delete_custom_line_items/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function DeleteBillGroup (obj, query) {
  return request({
    url: urlPrefix + 'delete_billing_group/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function CreatePricingPlanRule (obj, query) {
  return request({
    url: urlPrefix + 'create_pricing_plan_rule/',
    method: 'post',
    params: query,
    data: obj
  })
}

export function UpdateBillingGroup (obj, query) {
  return request({
    url: urlPrefix + 'update_billing_group/',
    method: 'post',
    params: query,
    data: obj
  })
}
export function ListAccountAssociations (query) {
  return request({
    url: urlPrefix + 'list_account_associations/',
    method: 'get',
    params: query
  })
}

export function ListPricingPlans (query) {
  return request({
    url: urlPrefix + 'list_pricing_plans/',
    method: 'get',
    params: query
  })
}

export function createBillingGroup (obj, query) {
  return request({
    url: urlPrefix + 'create_billing_group/',
    method: 'post',
    params: query,
    data: obj
  })
}
