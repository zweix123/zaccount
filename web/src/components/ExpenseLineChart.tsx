import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './ExpenseLineChart.css'

interface ExpenseLineChartProps {
  title: string
  data: number[]
  labels: string[]
  dataKey: string
  angle?: number // X轴标签角度
  interval?: number | 'preserveStartEnd' // X轴标签显示间隔
}

function ExpenseLineChart({ title, data, labels, dataKey, angle, interval }: ExpenseLineChartProps) {
  // 将数据转换为图表格式
  const chartData = data.map((value, index) => ({
    [dataKey]: value,
    label: labels[index] || `${index + 1}`,
  }))

  const formatValue = (value: number) => {
    return `¥${value.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }

  // 根据数据点数量自动调整底部边距
  const bottomMargin = angle ? 40 : 5

  return (
    <div className="expense-line-chart">
      <div className="expense-line-chart-header">
        <h3 className="expense-line-chart-title">{title}</h3>
      </div>
      <div className="expense-line-chart-body">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: bottomMargin }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="label" 
              angle={angle}
              interval={interval}
              tick={{ fontSize: 12 }}
            />
            <YAxis tickFormatter={(value) => `¥${(value / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value: number) => formatValue(value)} />
            <Legend />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke="#dc3545"
              strokeWidth={2}
              dot={{ r: data.length > 30 ? 2 : 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default ExpenseLineChart

