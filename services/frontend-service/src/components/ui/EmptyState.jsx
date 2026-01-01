import PropTypes from 'prop-types';
import './EmptyState.css';


function EmptyState( {
  icon,
  title,
  description,
  action,
  variant = 'default'
}) {
  const defaultIcon = (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" opacity="0.3"/>
      <circle cx="32" cy="32" r="20" fill="currentColor" opacity="0.05"/>
      <path d="M32 20V32L40 40" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.4"/>
      <circle cx="32" cy="32" r="3" fill="currentColor" opacity="0.4"/>
    </svg>
  );

  return (
    <div className={`empty-state empty-state--${variant}`}>
      <div className="empty-state__icon">
        {icon || defaultIcon}
      </div>
      <h3 className="empty-state__title">{title}</h3>
      {description && <p className="empty-state__description">{description}</p>}
      {action && <div className="empty-state__action">{action}</div>}
    </div>
  );
}

EmptyState.propTypes = {
  icon: PropTypes.node,
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  action: PropTypes.node,
  variant: PropTypes.oneOf(['default', 'card', 'inline'])
};

export default EmptyState;
