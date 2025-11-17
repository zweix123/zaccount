import './ConfirmButton.css'

interface ConfirmButtonProps {
  onClick: () => void
  disabled?: boolean
}

function ConfirmButton({ onClick, disabled = false }: ConfirmButtonProps) {
  return (
    <button
      className={`confirm-button ${disabled ? 'disabled' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      确认
    </button>
  )
}

export default ConfirmButton

