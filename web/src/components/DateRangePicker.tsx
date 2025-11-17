import './DateRangePicker.css'

interface DateRangePickerProps {
  startDate: string
  endDate: string
  onStartDateChange: (date: string) => void
  onEndDateChange: (date: string) => void
}

function DateRangePicker({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}: DateRangePickerProps) {
  return (
    <div className="date-range-picker">
      <label className="date-range-label">时间范围</label>
      <div className="date-range-inputs">
        <input
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
          className="date-input"
        />
        <span className="date-separator">至</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
          className="date-input"
        />
      </div>
    </div>
  )
}

export default DateRangePicker

