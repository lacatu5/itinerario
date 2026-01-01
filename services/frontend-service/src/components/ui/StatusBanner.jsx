import PropTypes from 'prop-types';
import './StatusBanner.css';


function StatusBanner( {
  type = 'error',
  message,
  onDismiss,
  icon
}) {
  const icons = {
    error: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M10 6V10M10 14H10.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    warning: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 2L19 18H1L10 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
        <path d="M10 8V11M10 14H10.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    success: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M6 10L9 13L14 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
    info: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M10 9V14M10 6H10.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    )
  };

  return (
    <div className={`status-banner status-banner--${type}`} role="alert">
      <span className="status-banner__icon">
        {icon || icons[type]}
      </span>
      <span className="status-banner__message">{message}</span>
      {onDismiss && (
        <button
          className="status-banner__dismiss"
          onClick={onDismiss}
          aria-label="Dismiss"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </button>
      )}
    </div>
  );
}

StatusBanner.propTypes = {
  type: PropTypes.oneOf(['error', 'warning', 'success', 'info']),
  message: PropTypes.string.isRequired,
  onDismiss: PropTypes.func,
  icon: PropTypes.node
};

export default StatusBanner;
