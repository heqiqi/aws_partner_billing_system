/*
 * @创建文件时间: 2021-06-08 10:40:32
 * @Auther: 猿小天
 * @最后修改人: 猿小天
 * @最后修改时间: 2021-06-09 10:36:20
 * 联系Qq:1638245306
 * @文件介绍: 操作日志
 */
import { request } from '@/api/service'

export const urlPrefix = '/api/system/login_log/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: query
  })
}
