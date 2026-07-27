import { mount } from '@vue/test-utils'

import type { LedgerMeta } from '@/types'

import EntryForm from './EntryForm.vue'

const meta: LedgerMeta = {
  accounts: ['银行卡', '微信'],
  tags: ['工作日'],
  dataFile: '/tmp/transaction.csv',
  categoryTree: {
    初始: {},
    收入: { 工资: {} },
    支出: { 餐饮: { 午饭: {} } },
    转入: { 内转: {} },
    转出: { 内转: {} },
  },
}

describe('EntryForm', () => {
  it('emits a user-visible entry intent', async () => {
    const wrapper = mount(EntryForm, {
      props: { meta, saving: false },
    })

    await wrapper.get('[data-testid="amount-input"]').setValue('28.5')
    await wrapper.get('[data-testid="account-input"]').setValue('微信')
    await wrapper.get('[data-testid="category-root"]').setValue('餐饮')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.emitted('save')).toHaveLength(1)
    expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({
      account: '微信',
      type: '支出',
      amount: 28.5,
      categories: ['餐饮'],
    })
  })

  it('keeps save disabled until required classification exists', async () => {
    const wrapper = mount(EntryForm, {
      props: { meta, saving: false },
    })

    await wrapper.get('[data-testid="amount-input"]').setValue('10')

    expect(
      wrapper.get('[data-testid="save-entry"]').attributes('disabled'),
    ).toBeDefined()
  })

  it('emits an initial balance without requiring a category', async () => {
    const wrapper = mount(EntryForm, {
      props: { meta, saving: false },
    })

    await wrapper.get('.type-初始').trigger('click')
    await wrapper.get('[data-testid="amount-input"]').setValue('500')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.find('[data-testid="category-root"]').exists()).toBe(false)
    expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({
      type: '初始',
      amount: 500,
      categories: [],
    })
  })
})
