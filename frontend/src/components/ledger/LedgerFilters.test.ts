import { mount } from '@vue/test-utils'

import { emptyFilters, type LedgerMeta } from '@/types'

import LedgerFilters from './LedgerFilters.vue'

const meta: LedgerMeta = {
  accounts: ['银行卡'],
  tags: ['旅行'],
  dataFile: '/tmp/transaction.csv',
  categoryTree: {
    收入: { 工资: {} },
    支出: { 餐饮: {} },
    转入: { 内转: {} },
    转出: { 内转: {} },
  },
}

describe('LedgerFilters', () => {
  it('applies description search through its public event', async () => {
    const wrapper = mount(LedgerFilters, {
      props: { filters: emptyFilters(), meta },
    })

    await wrapper.get('input[placeholder="搜索描述"]').setValue('咖啡')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.emitted('apply')?.[0]?.[0]).toMatchObject({
      query: '咖啡',
    })
  })
})
