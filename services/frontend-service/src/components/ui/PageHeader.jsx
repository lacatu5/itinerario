import PropTypes from 'prop-types';
import './PageHeader.css';


function PageHeader( {
  title,
  subtitle,
  action,
  children,
  variant = 'default'
}) {
  return (
    <header className={`page-header page-header--${variant}`}>
      <div className="page-header__content">
        <div className="page-header__text">
          <h1 className="page-header__title">{title}</h1>
          {subtitle && <p className="page-header__subtitle">{subtitle}</p>}
        </div>
        {action && <div className="page-header__action">{action}</div>}
      </div>
      {children && <div className="page-header__extra">{children}</div>}
    </header>
  );
}

PageHeader.propTypes = {
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  action: PropTypes.node,
  children: PropTypes.node,
  variant: PropTypes.oneOf(['default', 'gradient', 'minimal'])
};

export default PageHeader;
