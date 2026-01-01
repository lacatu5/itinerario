import { useEffect, useState } from 'react';
import '../../styles/itinerary-ui.css';
import { getCurrentUser } from '../../services/authStore';
import { getWeather, getTravelWarnings, getMyFlightTrackings, createFlightTracking, deleteFlightTracking, lookupFlightInfo } from '../../services/travelAlerts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faCloud,
  faSun,
  faCloudRain,
  faSnowflake,
  faBolt,
  faSmog,
  faWind,
  faDroplet,
  faTemperatureHigh,
  faExclamationTriangle,
  faPlane,
  faSearch,
  faMapMarkerAlt,
  faCalendarAlt,
  faPlus,
  faTrash,
  faTimes,
  faSync,
  faCheck,
  faClock,
  faBan,
  faLandmark,
  faPlaneDeparture
} from '@fortawesome/free-solid-svg-icons';

const WEATHER_ICONS = {
  0: faSun,
  1: faSun,
  2: faCloud,
  3: faCloud,
  45: faSmog,
  48: faSmog,
  51: faCloudRain,
  53: faCloudRain,
  55: faCloudRain,
  56: faCloudRain,
  57: faCloudRain,
  61: faCloudRain,
  63: faCloudRain,
  65: faCloudRain,
  66: faCloudRain,
  67: faCloudRain,
  71: faSnowflake,
  73: faSnowflake,
  75: faSnowflake,
  77: faSnowflake,
  80: faCloudRain,
  81: faCloudRain,
  82: faCloudRain,
  85: faSnowflake,
  86: faSnowflake,
  95: faBolt,
  96: faBolt,
  99: faBolt
};

const SEVERITY_COLORS = {
  low: '#10B981',
  medium: '#F59E0B',
  high: '#EF4444',
  critical: '#DC2626'
};

const FLIGHT_STATUS_CONFIG = {
  scheduled: { color: 'var(--color-medium-gray)', bgColor: '#F5F5F5', icon: faClock, label: 'Scheduled' },
  on_time: { color: 'var(--color-black)', bgColor: '#F5F5F5', icon: faCheck, label: 'On Time' },
  delayed: { color: '#D97706', bgColor: '#FEF3C7', icon: faClock, label: 'Delayed' },
  in_flight: { color: 'var(--color-black)', bgColor: '#F5F5F5', icon: faPlane, label: 'In Flight' },
  landed: { color: 'var(--color-black)', bgColor: '#F5F5F5', icon: faLandmark, label: 'Landed' },
  cancelled: { color: '#DC2626', bgColor: '#FEE2E2', icon: faBan, label: 'Cancelled' },
  diverted: { color: '#D97706', bgColor: '#FEF3C7', icon: faExclamationTriangle, label: 'Diverted' },
  boarding: { color: 'var(--color-black)', bgColor: '#F5F5F5', icon: faPlaneDeparture, label: 'Boarding' }
};

const getFlightStatusConfig = (status) => {
  return FLIGHT_STATUS_CONFIG[status] || FLIGHT_STATUS_CONFIG.scheduled;
};

function TravelAlerts() {
  const [user] = useState(getCurrentUser());
  const [activeTab, setActiveTab] = useState('weather');
  const [searchLocation, setSearchLocation] = useState('');
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [warningsLoading, setWarningsLoading] = useState(true);
  const [flightAlerts, setFlightAlerts] = useState([]);
  const [flightsLoading, setFlightsLoading] = useState(true);
  const [showFlightForm, setShowFlightForm] = useState(false);
  const [flightFormData, setFlightFormData] = useState( {
    flight_number: ''
  });
  const [flightLookupData, setFlightLookupData] = useState(null);
  const [flightFormLoading, setFlightFormLoading] = useState(false);
  const [flightLookupLoading, setFlightLookupLoading] = useState(false);
  const [flightFormError, setFlightFormError] = useState(null);

  useEffect(() => {
    loadWarnings();
    if (user) {
      loadFlightAlerts();
    } else {
      setFlightsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (activeTab === 'flights' && user && flightAlerts.length === 0 && !flightsLoading) {
      loadFlightAlerts();
    }
  }, [activeTab]);

  const loadWarnings = async () => {
    try {
      const res = await getTravelWarnings();
      setWarnings(res.warnings || []);
    } catch (e) {
      setWarnings([]);
    } finally {
      setWarningsLoading(false);
    }
  };

  const loadFlightAlerts = async () => {
    try {
      const res = await getMyFlightTrackings();
      setFlightAlerts(res.alerts || []);
    } catch (e) {
      setFlightAlerts([]);
    } finally {
      setFlightsLoading(false);
    }
  };

  const handleLookupFlight = async () => {
    if (!flightFormData.flight_number.trim()) return;

    setFlightLookupLoading(true);
    setFlightFormError(null);
    setFlightLookupData(null);

    try {
      const data = await lookupFlightInfo(flightFormData.flight_number.trim());
      setFlightLookupData(data);
    } catch (e) {
      setFlightFormError(e.response?.data?.detail || e.message || 'Flight not found. Please check the flight number.');
    } finally {
      setFlightLookupLoading(false);
    }
  };

  const handleAddFlight = async (e) => {
    e.preventDefault();

    if (!flightLookupData) {
      setFlightFormError('Please search for a flight first');
      return;
    }

    setFlightFormLoading(true);
    setFlightFormError(null);

    try {
      const flightData = {
        flight_number: flightLookupData.flight_number,
        airline: flightLookupData.airline,
        departure_airport: flightLookupData.departure_airport_iata || flightLookupData.departure_airport,
        arrival_airport: flightLookupData.arrival_airport_iata || flightLookupData.arrival_airport,
        scheduled_departure: flightLookupData.scheduled_departure,
        scheduled_arrival: flightLookupData.scheduled_arrival,
        status: flightLookupData.status || 'scheduled',
        gate: flightLookupData.gate,
        terminal: flightLookupData.terminal,
        delay_minutes: flightLookupData.delay_minutes
      };

      await createFlightTracking(flightData);
      await loadFlightAlerts();
      setShowFlightForm(false);
      setFlightFormData({ flight_number: '' });
      setFlightLookupData(null);
    } catch (e) {
      setFlightFormError(e.response?.data?.detail || e.message || 'Failed to add flight');
    } finally {
      setFlightFormLoading(false);
    }
  };

  const handleDeleteFlight = async (alertId) => {
    if (!window.confirm('Are you sure you want to remove this flight from tracking?')) return;

    try {
      await deleteFlightTracking(alertId);
      await loadFlightAlerts();
    } catch (e) {
      console.error('Failed to delete flight:', e);
    }
  };

  const handleWeatherSearch = async (e) => {
    e.preventDefault();
    if (!searchLocation.trim()) return;

    setWeatherLoading(true);
    setWeatherError(null);
    try {
      const data = await getWeather({ location: searchLocation.trim() });
      setWeather(data);
    } catch (e) {
      setWeatherError(e.message || 'Failed to fetch weather data');
      setWeather(null);
    } finally {
      setWeatherLoading(false);
    }
  };

  const getWeatherIcon = (code) => {
    return WEATHER_ICONS[code] || faCloud;
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateStr) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          <div style={ {
            marginBottom: 32,
            padding: 32,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            <h1 style={ {
              fontSize: '2.5rem',
              fontWeight: 700,
              color: 'var(--color-black)',
              marginBottom: 8,
              lineHeight: 1.2
            }}>
              Travel Alerts
            </h1>
            <p style={ {
              color: 'var(--color-medium-gray)',
              fontSize: '1.1rem',
              fontWeight: 500,
              margin: 0
            }}>
              Weather forecasts, travel warnings, and flight information
            </p>
          </div>

          <div style={ {
            display: 'flex',
            gap: 8,
            marginBottom: 24,
            padding: 4,
            backgroundColor: '#F5F5F5',
            borderRadius: 'var(--radius-md)'
          }}>
            {[
              { key: 'weather', icon: faCloud, label: 'Weather' },
              { key: 'warnings', icon: faExclamationTriangle, label: 'Warnings' },
              { key: 'flights', icon: faPlane, label: 'Flights' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                style={ {
                  flex: 1,
                  padding: '12px 16px',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: activeTab === tab.key ? '#FFFFFF' : 'transparent',
                  color: activeTab === tab.key ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  boxShadow: activeTab === tab.key ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                }}
              >
                <FontAwesomeIcon icon={tab.icon} />
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'weather' && (
            <div>
              <form onSubmit={handleWeatherSearch} style={{ marginBottom: 24 }}>
                <div style={ {
                  display: 'flex',
                  gap: 12,
                  alignItems: 'stretch'
                }}>
                  <div style={{ flex: 1, position: 'relative' }}>
                    <FontAwesomeIcon
                      icon={faMapMarkerAlt}
                      style={ {
                        position: 'absolute',
                        left: 16,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: 'var(--color-light-gray)'
                      }}
                    />
                    <input
                      type="text"
                      className="ui-input"
                      placeholder="Enter city or destination..."
                      value={searchLocation}
                      onChange={(e) => setSearchLocation(e.target.value)}
                      style={{ paddingLeft: 44 }}
                    />
                  </div>
                  <button
                    type="submit"
                    className="ui-button"
                    disabled={weatherLoading || !searchLocation.trim()}
                    style={{ display: 'flex', alignItems: 'center', gap: 8 }}
                  >
                    <FontAwesomeIcon icon={faSearch} />
                    Search
                  </button>
                </div>
              </form>

              {weatherLoading && (
                <div style={ {
                  textAlign: 'center',
                  padding: 40,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <p className="ui-help">Loading weather data...</p>
                </div>
              )}

              {weatherError && (
                <div style={ {
                  padding: 16,
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA',
                  borderRadius: 'var(--radius-md)',
                  color: '#DC2626',
                  marginBottom: 24
                }}>
                  {weatherError}
                </div>
              )}

              {weather && (
                <div>
                  <div style={ {
                    padding: 32,
                    backgroundColor: '#FFFFFF',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid #F0F0F0',
                    marginBottom: 24
                  }}>
                    <div style={ {
                      display: 'flex',
                      alignItems: 'center',
                      gap: 24,
                      marginBottom: 24
                    }}>
                      <div style={ {
                        width: 80,
                        height: 80,
                        backgroundColor: '#F0F9FF',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '2.5rem',
                        color: '#0EA5E9'
                      }}>
                        <FontAwesomeIcon icon={getWeatherIcon(weather.current.weather_code)} />
                      </div>
                      <div>
                        <h2 style={ {
                          fontSize: '1.75rem',
                          fontWeight: 700,
                          color: 'var(--color-black)',
                          marginBottom: 4
                        }}>
                          {weather.current.location_name || searchLocation}
                        </h2>
                        <p style={ {
                          color: 'var(--color-medium-gray)',
                          fontSize: '1.1rem',
                          margin: 0
                        }}>
                          {weather.current.weather_description}
                        </p>
                      </div>
                    </div>

                    <div style={ {
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                      gap: 20
                    }}>
                      <div style={ {
                        textAlign: 'center',
                        padding: 16,
                        backgroundColor: '#FAFBFC',
                        borderRadius: 'var(--radius-md)'
                      }}>
                        <FontAwesomeIcon icon={faTemperatureHigh} style={{ color: '#EF4444', marginBottom: 8, fontSize: '1.25rem' }} />
                        <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-black)' }}>
                          {Math.round(weather.current.temperature)}°C
                        </div>
                        <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>Temperature</div>
                      </div>
                      <div style={ {
                        textAlign: 'center',
                        padding: 16,
                        backgroundColor: '#FAFBFC',
                        borderRadius: 'var(--radius-md)'
                      }}>
                        <FontAwesomeIcon icon={faTemperatureHigh} style={{ color: '#F97316', marginBottom: 8, fontSize: '1.25rem' }} />
                        <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-black)' }}>
                          {Math.round(weather.current.feels_like)}°C
                        </div>
                        <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>Feels Like</div>
                      </div>
                      <div style={ {
                        textAlign: 'center',
                        padding: 16,
                        backgroundColor: '#FAFBFC',
                        borderRadius: 'var(--radius-md)'
                      }}>
                        <FontAwesomeIcon icon={faDroplet} style={{ color: '#3B82F6', marginBottom: 8, fontSize: '1.25rem' }} />
                        <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-black)' }}>
                          {weather.current.humidity}%
                        </div>
                        <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>Humidity</div>
                      </div>
                      <div style={ {
                        textAlign: 'center',
                        padding: 16,
                        backgroundColor: '#FAFBFC',
                        borderRadius: 'var(--radius-md)'
                      }}>
                        <FontAwesomeIcon icon={faWind} style={{ color: '#6366F1', marginBottom: 8, fontSize: '1.25rem' }} />
                        <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-black)' }}>
                          {Math.round(weather.current.wind_speed)} km/h
                        </div>
                        <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>Wind</div>
                      </div>
                    </div>
                  </div>

                  {weather.daily_forecast && weather.daily_forecast.length > 0 && (
                    <div style={ {
                      padding: 24,
                      backgroundColor: '#FFFFFF',
                      borderRadius: 'var(--radius-lg)',
                      border: '1px solid #F0F0F0'
                    }}>
                      <h3 style={ {
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 16
                      }}>
                        7-Day Forecast
                      </h3>
                      <div style={ {
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
                        gap: 12
                      }}>
                        {weather.daily_forecast.map((day, idx) => (
                          <div
                            key={idx}
                            style={ {
                              textAlign: 'center',
                              padding: 16,
                              backgroundColor: '#FAFBFC',
                              borderRadius: 'var(--radius-md)',
                              border: '1px solid #F0F0F0'
                            }}
                          >
                            <div style={ {
                              fontSize: '0.85rem',
                              fontWeight: 600,
                              color: 'var(--color-medium-gray)',
                              marginBottom: 8
                            }}>
                              {formatDate(day.date)}
                            </div>
                            <FontAwesomeIcon
                              icon={getWeatherIcon(day.weather_code)}
                              style={ {
                                fontSize: '1.5rem',
                                color: '#0EA5E9',
                                marginBottom: 8
                              }}
                            />
                            <div style={ {
                              fontSize: '1rem',
                              fontWeight: 700,
                              color: 'var(--color-black)'
                            }}>
                              {Math.round(day.temperature_max)}°
                            </div>
                            <div style={ {
                              fontSize: '0.9rem',
                              color: 'var(--color-light-gray)'
                            }}>
                              {Math.round(day.temperature_min)}°
                            </div>
                            <div style={ {
                              fontSize: '0.75rem',
                              color: '#3B82F6',
                              marginTop: 4
                            }}>
                              <FontAwesomeIcon icon={faDroplet} style={{ marginRight: 4 }} />
                              {day.precipitation_probability}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {!weather && !weatherLoading && !weatherError && (
                <div style={ {
                  textAlign: 'center',
                  padding: 64,
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    background: 'linear-gradient(135deg, #f0f0f0 0%, #fafafa 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 24px',
                    fontSize: '2rem',
                    color: 'var(--color-medium-gray)'
                  }}>
                    <FontAwesomeIcon icon={faCloud} />
                  </div>
                  <h3 style={{ fontWeight: 700, color: 'var(--color-black)', fontSize: '1.5rem', marginBottom: 8 }}>
                    Search for Weather
                  </h3>
                  <p style={ {
                    color: 'var(--color-light-gray)',
                    fontSize: '1rem',
                    maxWidth: 400,
                    margin: '0 auto'
                  }}>
                    Enter a city or destination to get current weather conditions and a 7-day forecast.
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'warnings' && (
            <div>
              {warningsLoading ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 40,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <p className="ui-help">Loading travel warnings...</p>
                </div>
              ) : warnings.length === 0 ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 64,
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    background: 'linear-gradient(135deg, #f0f0f0 0%, #fafafa 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 24px',
                    fontSize: '2rem',
                    color: '#10B981'
                  }}>
                    <FontAwesomeIcon icon={faExclamationTriangle} />
                  </div>
                  <h3 style={{ fontWeight: 700, color: 'var(--color-black)', fontSize: '1.5rem', marginBottom: 8 }}>
                    No Active Warnings
                  </h3>
                  <p style={ {
                    color: 'var(--color-light-gray)',
                    fontSize: '1rem',
                    maxWidth: 400,
                    margin: '0 auto'
                  }}>
                    There are currently no travel warnings or advisories to display.
                  </p>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: 16 }}>
                  {warnings.map((warning) => (
                    <div
                      key={warning.id}
                      style={ {
                        padding: 24,
                        backgroundColor: '#FFFFFF',
                        borderRadius: 'var(--radius-lg)',
                        border: '1px solid #F0F0F0',
                        borderLeft: `4px solid ${SEVERITY_COLORS[warning.severity] || '#6B7280'}`
                      }}
                    >
                      <div style={ {
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: 12
                      }}>
                        <div>
                          <h3 style={ {
                            fontSize: '1.25rem',
                            fontWeight: 700,
                            color: 'var(--color-black)',
                            marginBottom: 4
                          }}>
                            {warning.title}
                          </h3>
                          <div style={ {
                            display: 'flex',
                            alignItems: 'center',
                            gap: 12,
                            flexWrap: 'wrap'
                          }}>
                            <span style={ {
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 6,
                              fontSize: '0.9rem',
                              color: 'var(--color-medium-gray)'
                            }}>
                              <FontAwesomeIcon icon={faMapMarkerAlt} />
                              {warning.country_name}
                              {warning.region && `, ${warning.region}`}
                            </span>
                            <span style={ {
                              padding: '4px 10px',
                              backgroundColor: `${SEVERITY_COLORS[warning.severity]}20`,
                              color: SEVERITY_COLORS[warning.severity],
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.8rem',
                              fontWeight: 600,
                              textTransform: 'uppercase'
                            }}>
                              {warning.severity}
                            </span>
                            <span style={ {
                              padding: '4px 10px',
                              backgroundColor: '#F3F4F6',
                              color: 'var(--color-medium-gray)',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.8rem',
                              fontWeight: 500
                            }}>
                              {warning.category}
                            </span>
                          </div>
                        </div>
                      </div>
                      <p style={ {
                        color: 'var(--color-medium-gray)',
                        fontSize: '0.95rem',
                        lineHeight: 1.6,
                        margin: 0
                      }}>
                        {warning.description}
                      </p>
                      {warning.source_url && (
                        <a
                          href={warning.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={ {
                            display: 'inline-block',
                            marginTop: 12,
                            color: 'var(--color-black)',
                            fontSize: '0.9rem',
                            fontWeight: 500,
                            textDecoration: 'underline'
                          }}
                        >
                          View Source →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'flights' && (
            <div>
              {!user ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 64,
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    background: 'linear-gradient(135deg, #f0f0f0 0%, #fafafa 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 24px',
                    fontSize: '2rem',
                    color: 'var(--color-medium-gray)'
                  }}>
                    <FontAwesomeIcon icon={faPlane} />
                  </div>
                  <h3 style={{ fontWeight: 700, color: 'var(--color-black)', fontSize: '1.5rem', marginBottom: 8 }}>
                    Sign In Required
                  </h3>
                  <p style={ {
                    color: 'var(--color-light-gray)',
                    fontSize: '1rem',
                    maxWidth: 400,
                    margin: '0 auto'
                  }}>
                    Please sign in to view and manage your flight alerts.
                  </p>
                </div>
              ) : flightsLoading ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 40,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <p className="ui-help">Loading flight alerts...</p>
                </div>
              ) : (
                <>
                  {}
                  <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                    <span style={ {
                      fontSize: '0.85rem',
                      color: 'var(--color-medium-gray)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6
                    }}>
                      <FontAwesomeIcon icon={faSync} />
                      Status updates every 30 minutes
                    </span>
                    <button
                      onClick={() => setShowFlightForm(!showFlightForm)}
                      className="ui-button"
                      style={{ display: 'flex', alignItems: 'center', gap: 8 }}
                    >
                      <FontAwesomeIcon icon={showFlightForm ? faTimes : faPlus} />
                      {showFlightForm ? 'Cancel' : 'Track a Flight'}
                    </button>
                  </div>

                  {}
                  {showFlightForm && (
                    <div style={ {
                      padding: 24,
                      backgroundColor: '#FFFFFF',
                      borderRadius: 'var(--radius-lg)',
                      border: '1px solid #F0F0F0',
                      marginBottom: 24
                    }}>
                      <h3 style={ {
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 8
                      }}>
                        Track a Flight
                      </h3>
                      <p style={ {
                        color: 'var(--color-medium-gray)',
                        fontSize: '0.9rem',
                        marginBottom: 16
                      }}>
                        Enter the flight number and we'll automatically fetch the flight details.
                      </p>

                      {flightFormError && (
                        <div style={ {
                          padding: 12,
                          backgroundColor: '#FEF2F2',
                          border: '1px solid #FECACA',
                          borderRadius: 'var(--radius-md)',
                          color: '#DC2626',
                          marginBottom: 16
                        }}>
                          {flightFormError}
                        </div>
                      )}

                      {}
                      <div style={{ marginBottom: 16 }}>
                        <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: '0.9rem' }}>
                          Flight Number *
                        </label>
                        <div style={{ display: 'flex', gap: 12 }}>
                          <input
                            type="text"
                            className="ui-input"
                            placeholder="e.g., IB3170, AA8609, BA123"
                            value={flightFormData.flight_number}
                            onChange={(e) => {
                              setFlightFormData({ flight_number: e.target.value.toUpperCase() });
                              setFlightLookupData(null);
                              setFlightFormError(null);
                            }}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault();
                                handleLookupFlight();
                              }
                            }}
                            style={{ flex: 1 }}
                          />
                          <button
                            type="button"
                            onClick={handleLookupFlight}
                            className="ui-button"
                            disabled={flightLookupLoading || !flightFormData.flight_number.trim()}
                            style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 120 }}
                          >
                            <FontAwesomeIcon icon={faSearch} spin={flightLookupLoading} />
                            {flightLookupLoading ? 'Searching...' : 'Search'}
                          </button>
                        </div>
                      </div>

                      {}
                      {flightLookupData && (
                        <div style={ {
                          padding: 20,
                          backgroundColor: '#FFFFFF',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid #F0F0F0',
                          marginBottom: 16
                        }}>
                          <div style={ {
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            marginBottom: 12,
                            color: 'var(--color-black)'
                          }}>
                            <FontAwesomeIcon icon={faCheck} />
                            <span style={{ fontWeight: 600 }}>Flight Found!</span>
                          </div>

                          <div style={ {
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: 16,
                            backgroundColor: '#FFFFFF',
                            borderRadius: 'var(--radius-md)',
                            gap: 16
                          }}>
                            <div style={{ textAlign: 'center', flex: 1 }}>
                              <div style={ {
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                color: 'var(--color-black)',
                                marginBottom: 4
                              }}>
                                {flightLookupData.departure_airport_iata || '---'}
                              </div>
                              <div style={ {
                                fontSize: '0.8rem',
                                color: 'var(--color-medium-gray)',
                                maxWidth: 120,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}>
                                {flightLookupData.departure_airport?.split('(')[0]?.trim() || ''}
                              </div>
                              <div style={ {
                                fontSize: '0.85rem',
                                color: 'var(--color-black)',
                                fontWeight: 500,
                                marginTop: 4
                              }}>
                                {flightLookupData.scheduled_departure ? formatDateTime(flightLookupData.scheduled_departure) : '---'}
                              </div>
                            </div>

                            <div style={{ textAlign: 'center', padding: '0 16px' }}>
                              <div style={ {
                                fontSize: '1rem',
                                fontWeight: 700,
                                color: 'var(--color-black)',
                                marginBottom: 4
                              }}>
                                {flightLookupData.flight_number}
                              </div>
                              <FontAwesomeIcon
                                icon={faPlane}
                                style={ {
                                  fontSize: '1.25rem',
                                  color: 'var(--color-medium-gray)',
                                  transform: 'rotate(90deg)'
                                }}
                              />
                              <div style={ {
                                fontSize: '0.8rem',
                                color: 'var(--color-medium-gray)',
                                marginTop: 4
                              }}>
                                {flightLookupData.airline || ''}
                              </div>
                            </div>

                            <div style={{ textAlign: 'center', flex: 1 }}>
                              <div style={ {
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                color: 'var(--color-black)',
                                marginBottom: 4
                              }}>
                                {flightLookupData.arrival_airport_iata || '---'}
                              </div>
                              <div style={ {
                                fontSize: '0.8rem',
                                color: 'var(--color-medium-gray)',
                                maxWidth: 120,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}>
                                {flightLookupData.arrival_airport?.split('(')[0]?.trim() || ''}
                              </div>
                              <div style={ {
                                fontSize: '0.85rem',
                                color: 'var(--color-black)',
                                fontWeight: 500,
                                marginTop: 4
                              }}>
                                {flightLookupData.scheduled_arrival ? formatDateTime(flightLookupData.scheduled_arrival) : '---'}
                              </div>
                            </div>
                          </div>

                          {}
                          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                            {(() => {
                              const statusConfig = getFlightStatusConfig(flightLookupData.status);
                              return (
                                <span style={ {
                                  padding: '4px 12px',
                                  backgroundColor: statusConfig.bgColor,
                                  color: statusConfig.color,
                                  borderRadius: 'var(--radius-sm)',
                                  fontSize: '0.85rem',
                                  fontWeight: 600,
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 6
                                }}>
                                  <FontAwesomeIcon icon={statusConfig.icon} />
                                  {statusConfig.label}
                                </span>
                              );
                            })()}
                            {flightLookupData.delay_minutes > 0 && (
                              <span style={ {
                                padding: '4px 12px',
                                backgroundColor: '#FEF3C7',
                                color: '#D97706',
                                borderRadius: 'var(--radius-sm)',
                                fontSize: '0.85rem',
                                fontWeight: 600
                              }}>
                                +{flightLookupData.delay_minutes} min delay
                              </span>
                            )}
                            {flightLookupData.gate && (
                              <span style={ {
                                fontSize: '0.85rem',
                                color: 'var(--color-medium-gray)'
                              }}>
                                Gate: {flightLookupData.gate}
                              </span>
                            )}
                            {flightLookupData.terminal && (
                              <span style={ {
                                fontSize: '0.85rem',
                                color: 'var(--color-medium-gray)'
                              }}>
                                Terminal: {flightLookupData.terminal}
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                        <button
                          type="button"
                          onClick={() => {
                            setShowFlightForm(false);
                            setFlightFormData({ flight_number: '' });
                            setFlightLookupData(null);
                            setFlightFormError(null);
                          }}
                          className="ui-button ui-button-secondary"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={handleAddFlight}
                          className="ui-button"
                          disabled={flightFormLoading || !flightLookupData}
                          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
                        >
                          <FontAwesomeIcon icon={faPlus} />
                          {flightFormLoading ? 'Adding...' : 'Track This Flight'}
                        </button>
                      </div>
                    </div>
                  )}

                  {}
                  {flightAlerts.length === 0 ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 64,
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    background: 'linear-gradient(135deg, #f0f0f0 0%, #fafafa 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 24px',
                    fontSize: '2rem',
                    color: 'var(--color-medium-gray)'
                  }}>
                    <FontAwesomeIcon icon={faPlane} />
                  </div>
                  <h3 style={{ fontWeight: 700, color: 'var(--color-black)', fontSize: '1.5rem', marginBottom: 8 }}>
                    No Flight Alerts
                  </h3>
                  <p style={ {
                    color: 'var(--color-light-gray)',
                    fontSize: '1rem',
                    maxWidth: 400,
                    margin: '0 auto'
                  }}>
                    You haven't added any flights to track yet. Click "Track a Flight" above to get started.
                  </p>
                </div>
                  ) : (
                <div style={{ display: 'grid', gap: 16 }}>
                  {flightAlerts.map((flight) => {
                    const statusConfig = getFlightStatusConfig(flight.status);
                    const isAlertStatus = flight.status === 'delayed' || flight.status === 'cancelled' || flight.status === 'diverted';
                    return (
                    <div
                      key={flight.id}
                      style={ {
                        padding: 24,
                        backgroundColor: '#FFFFFF',
                        borderRadius: 'var(--radius-lg)',
                        border: '1px solid #F0F0F0',
                        borderLeft: isAlertStatus ? `4px solid ${statusConfig.color}` : '1px solid #F0F0F0'
                      }}
                    >
                      <div style={ {
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: 16
                      }}>
                        <div>
                          <h3 style={ {
                            fontSize: '1.25rem',
                            fontWeight: 700,
                            color: 'var(--color-black)',
                            marginBottom: 4
                          }}>
                            {flight.flight_number}
                            {flight.airline && ` - ${flight.airline}`}
                          </h3>
                          <span style={ {
                            padding: '4px 10px',
                            backgroundColor: statusConfig.bgColor,
                            color: statusConfig.color,
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6
                          }}>
                            <FontAwesomeIcon icon={statusConfig.icon} />
                            {statusConfig.label}
                          </span>
                        </div>
                        {flight.delay_minutes > 0 && (
                          <span style={ {
                            padding: '4px 10px',
                            backgroundColor: '#FEF3C7',
                            color: '#D97706',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.85rem',
                            fontWeight: 600
                          }}>
                            +{flight.delay_minutes} min
                          </span>
                        )}
                      </div>

                      <div style={ {
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: 16,
                        backgroundColor: '#FAFBFC',
                        borderRadius: 'var(--radius-md)',
                        gap: 16
                      }}>
                        <div style={{ textAlign: 'center', flex: 1 }}>
                          <div style={ {
                            fontSize: '1.5rem',
                            fontWeight: 700,
                            color: 'var(--color-black)',
                            marginBottom: 4
                          }}>
                            {flight.departure_airport}
                          </div>
                          <div style={ {
                            fontSize: '0.9rem',
                            color: 'var(--color-medium-gray)'
                          }}>
                            {formatDateTime(flight.scheduled_departure)}
                          </div>
                          {flight.terminal && (
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-light-gray)' }}>
                              Terminal {flight.terminal}
                            </div>
                          )}
                        </div>

                        <div style={{ textAlign: 'center' }}>
                          <FontAwesomeIcon
                            icon={faPlane}
                            style={ {
                              fontSize: '1.25rem',
                              color: 'var(--color-medium-gray)',
                              transform: 'rotate(90deg)'
                            }}
                          />
                        </div>

                        <div style={{ textAlign: 'center', flex: 1 }}>
                          <div style={ {
                            fontSize: '1.5rem',
                            fontWeight: 700,
                            color: 'var(--color-black)',
                            marginBottom: 4
                          }}>
                            {flight.arrival_airport}
                          </div>
                          <div style={ {
                            fontSize: '0.9rem',
                            color: 'var(--color-medium-gray)'
                          }}>
                            {formatDateTime(flight.scheduled_arrival)}
                          </div>
                          {flight.gate && (
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-light-gray)' }}>
                              Gate {flight.gate}
                            </div>
                          )}
                        </div>
                      </div>

                      {flight.alert_message && (
                        <div style={ {
                          marginTop: 12,
                          padding: 12,
                          backgroundColor: '#F5F5F5',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.9rem',
                          color: 'var(--color-black)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 8
                        }}>
                          <FontAwesomeIcon icon={faExclamationTriangle} style={{ color: statusConfig.color }} />
                          {flight.alert_message}
                        </div>
                      )}

                      {}
                      <div style={{ marginTop: 12, display: 'flex', justifyContent: 'flex-end' }}>
                        <button
                          onClick={() => handleDeleteFlight(flight.id)}
                          style={ {
                            padding: '6px 12px',
                            border: 'none',
                            borderRadius: 'var(--radius-sm)',
                            backgroundColor: 'transparent',
                            color: '#DC2626',
                            fontSize: '0.85rem',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6
                          }}
                        >
                          <FontAwesomeIcon icon={faTrash} />
                          Remove
                        </button>
                      </div>
                    </div>
                    );
                  })}
                </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TravelAlerts;
