import PropTypes from 'prop-types';
import './StatsGrid.css';


function StatsGrid({ stats }) {
  return (
    <div className="stats-grid">
      {stats.map((stat, index) => (
        <div key={index} className="stats-grid__item">
          {stat.icon && <div className="stats-grid__icon">{stat.icon}</div>}
          <div className="stats-grid__value">{stat.value}</div>
          <div className="stats-grid__label">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}

StatsGrid.propTypes = {
  stats: PropTypes.arrayOf(
    PropTypes.shape( {
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      label: PropTypes.string.isRequired,
      icon: PropTypes.node
    })
  ).isRequired
};

export default StatsGrid;
