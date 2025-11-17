import './StatCard.css'

interface StatCardProps {
  title: string
  value: number
  type: 'income' | 'expense' | 'balance'
}

function StatCard({ title, value, type }: StatCardProps) {
  const formatValue = (val: number) => {
    return val.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  return (
    <div className={`stat-card stat-card-${type}`}>
      <div className="stat-card-header">
        <h3 className="stat-card-title">{title}</h3>
      </div>
      <div className="stat-card-body">
        <div className="stat-card-value">¥{formatValue(value)}</div>
      </div>
    </div>
  )
}

export default StatCard

