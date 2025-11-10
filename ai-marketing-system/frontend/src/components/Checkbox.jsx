import './Checkbox.css'

export default function Checkbox({ id, checked, onChange, className = '', ...props }) {
  return (
    <input
      type="checkbox"
      id={id}
      checked={checked}
      onChange={onChange}
      className={`custom-checkbox ${className}`}
      style={{
        backgroundColor: checked ? '#2563eb' : '#ffffff',
        borderColor: checked ? '#2563eb' : '#d1d5db',
      }}
      {...props}
    />
  )
}