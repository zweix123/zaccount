import { useState, useEffect } from 'react'
import DateRangePicker from '../components/DateRangePicker'
import FilterForm from '../components/FilterForm'
import ConfirmButton from '../components/ConfirmButton'
import StatCard from '../components/StatCard'
import './Display.css'

interface DisplayData {
  income: number
  expense: number
  balance: number
  start_date: string
  end_date: string
}

interface ConfigInitData {
  earliest_date: string
  latest_date: string
}

function Display() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [data, setData] = useState<DisplayData | null>(null)
  const [loading, setLoading] = useState(false)
  const [initLoading, setInitLoading] = useState(true)

  // 初始化日期范围（从后端获取）
  useEffect(() => {
    const fetchInitData = async () => {
      try {
        const response = await fetch('/api/config/init')
        if (!response.ok) {
          throw new Error('获取初始化数据失败')
        }
        const initData: ConfigInitData = await response.json()
        setStartDate(initData.earliest_date)
        setEndDate(initData.latest_date)
      } catch (error) {
        console.error('Error fetching init data:', error)
        // 如果获取失败，使用默认值（最近30天）
        const today = new Date()
        const thirtyDaysAgo = new Date(today)
        thirtyDaysAgo.setDate(today.getDate() - 30)

        const formatDate = (date: Date) => {
          return date.toISOString().split('T')[0]
        }

        setEndDate(formatDate(today))
        setStartDate(formatDate(thirtyDaysAgo))
      } finally {
        setInitLoading(false)
      }
    }

    fetchInitData()
  }, [])

  const handleConfirm = async () => {
    if (!startDate || !endDate) {
      alert('请选择时间范围')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(
        `/api/display/common?start_date=${startDate}&end_date=${endDate}`
      )
      if (!response.ok) {
        throw new Error('获取数据失败')
      }
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Error fetching data:', error)
      alert('获取数据失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="display-page">
      <div className="display-controls">
        <DateRangePicker
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
        />
        <FilterForm />
        <ConfirmButton onClick={handleConfirm} disabled={loading || initLoading} />
      </div>

      {data && (
        <div className="display-cards">
          <StatCard title="增加" value={data.income} type="income" />
          <StatCard title="减少" value={data.expense} type="expense" />
          <StatCard title="结余" value={data.balance} type="balance" />
        </div>
      )}
    </div>
  )
}

export default Display
