export const crudOptions = vm => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      tableType: 'vxe-table',
      rowKey: true, // 必须设置，true or false
      rowId: 'id',
      height: '100%', // 表格高度100%, 使用toolbar必须设置
      highlightCurrentRow: false
    },
    rowHandle: {
      width: 140,
      view: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Retrieve')
        }
      },
      edit: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      }
    },
    indexRow: {
      // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 100
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 24, // 默认的表单 span
      width: '35%'
    },
    columns: [{
      title: 'ID',
      key: 'id',
      show: false,
      disabled: true,
      width: 90,
      form: {
        disabled: true
      }
    },
    {
      title: '商品',
      key: 'goods',
      sortable: true,
      treeNode: true,

      type: 'input',
      form: {
        editDisabled: true,
        rules: [
          // 表单校验规则
          { required: true, message: '商品名称必填' }
        ],
        component: {
          props: {
            clearable: true
          },
          placeholder: '请输入商品'
        },
        itemProps: {
          class: { yxtInput: true }
        }
      }
    },
    {
      title: '库存量',
      key: 'inventory',
      sortable: true,
      type: 'number',
      form: {
        editDisabled: true,
        rules: [
          // 表单校验规则
          { required: true, message: '库存量必填' }
        ],
        component: {
          props: {
            clearable: true
          },
          placeholder: '请输入库存量'
        },
        itemProps: {
          class: { yxtInput: true }
        }
      }
    },
    {
      title: '商品定价',
      key: 'goods_price',
      sortable: true,

      search: {
        component: {
          props: {
            clearable: true
          }
        }
      },

      type: 'number',
      form: {
        editDisabled: true,
        rules: [
          // 表单校验规则
          { required: true, message: '商品定价必填' }
        ],
        component: {
          props: {
            clearable: true
          },
          placeholder: '请输入商品定价'
        },
        itemProps: {
          class: { yxtInput: true }
        }
      }
    },
    {
      title: '进货时间',
      key: 'purchase_goods_date',
      sortable: true,
      type: 'date',
      form: {
        rules: [
          { required: true, message: '进货时间必填' }
        ],
        component: {
          props: {
            clearable: true,
            format: 'yyyy-MM-dd',
            valueFormat: 'yyyy-MM-dd'
          },
          placeholder: '请输入进货时间'
        },
        itemProps: {
          class: { yxtInput: true }
        }
      }
    }
    ].concat(vm.commonEndColumns())
  }
}
