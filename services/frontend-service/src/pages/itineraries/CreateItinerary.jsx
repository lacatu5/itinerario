import { useState } from 'react';
import { createPortal } from 'react-dom';
import '../../styles/itinerary-ui.css';
import { createItinerary } from '../../services/itineraries';
import { getCurrentUser } from '../../services/authStore';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlane, faMapMarkerAlt, faCalendarAlt, faSave, faMap, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import MapPicker from '../../components/MapPicker';
import { PageHeader, StatusBanner } from '../../components/ui';
import { getTravelWarnings } from '../../services/travelAlerts';

function CreateItinerary() {
  const navigate = useNavigate();
  const [form, setForm] = useState( {
    title: '',
    destination: '',
    start_date: '',
    end_date: '',
    short_description: '',
    detail_description: '',
    latitude: '',
    longitude: '',
    address: '',
    country_code: ''
  });
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showMap, setShowMap] = useState(true);
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [travelWarnings, setTravelWarnings] = useState([]);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const mapValue = form.latitude && form.longitude ? {
    lat: parseFloat(form.latitude),
    lng: parseFloat(form.longitude),
    address: form.address
  } : null;

  const handleMapChange = (locationData) => {
    console.log('📍 MapPicker location data:', locationData);
    if (locationData) {
      const destParts = [];
      if (locationData.city) destParts.push(locationData.city);
      if (locationData.region) destParts.push(locationData.region);
      if (locationData.country) destParts.push(locationData.country);

      const destination = destParts.length > 0
        ? destParts.join(', ')
        : locationData.name || '';

      setForm( {
        ...form,
        destination: destination,
        latitude: String(locationData.lat),
        longitude: String(locationData.lng),
        address: locationData.address || '',
        country_code: locationData.country_code || ''
      });
      console.log('Form updated with country_code:', locationData.country_code);
    } else {
      setForm( {
        ...form,
        destination: '',
        latitude: '',
        longitude: '',
        address: '',
        country_code: ''
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    const user = getCurrentUser();
    if (!user) {
      setMessage({ type: 'error', text: 'Please register first to create itineraries.' });
      return;
    }
    if (!form.title || !form.destination || !form.start_date) {
      setMessage({ type: 'error', text: 'Title, destination and start date are required.' });
      return;
    }
    if (form.short_description.length > 80) {
      setMessage({ type: 'error', text: 'Short description max 80 characters.' });
      return;
    }

    const tripDate = new Date(form.start_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const isFutureTrip = tripDate >= today;

    console.log('Debug Info:', {
      country_code: form.country_code,
      start_date: form.start_date,
      tripDate: tripDate.toISOString(),
      today: today.toISOString(),
      isFutureTrip,
      shouldCheckWarnings: form.country_code && isFutureTrip
    });

    if (form.country_code && isFutureTrip) {
      try {
        console.log('Fetching travel warnings for:', form.country_code);
        const warningsResponse = await getTravelWarnings(form.country_code);
        console.log('Warnings response:', warningsResponse);
        const warnings = warningsResponse?.warnings || [];
        console.log('Total warnings:', warnings.length);

        const severeWarnings = warnings.filter(w =>
          w.active && ['critical', 'high', 'extreme', 'severe'].includes(w.severity?.toLowerCase())
        );
        console.log('Severe warnings:', severeWarnings.length, severeWarnings);

        if (severeWarnings.length > 0) {
          setTravelWarnings(severeWarnings);
          setShowWarningModal(true);
          console.log('Showing warning modal');
          return;
        }
      } catch (err) {
        console.error('Error checking travel warnings:', err);
      }
    }

    await submitItinerary();
  };

  const submitItinerary = async () => {
    setLoading(true);
    const user = getCurrentUser();
    try {
      const payload = {
        title: form.title,
        destination: form.destination,
        start_date: form.start_date,
        end_date: form.end_date,
        short_description: form.short_description,
        detail_description: form.detail_description,
        latitude: form.latitude || null,
        longitude: form.longitude || null,
        address: form.address || null
      };
      const created = await createItinerary(payload);
      if (created && created.id) {
        navigate(`/itineraries/${created.id}`);
        return;
      }
      setMessage({ type: 'success', text: 'Itinerary saved successfully.' });
      setForm({ title: '', destination: '', start_date: '', end_date: '', short_description: '', detail_description: '', latitude: '', longitude: '', address: '', country_code: '' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Error saving itinerary.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          <PageHeader
            title="Create Itinerary"
            subtitle="Design your next trip in detail"
          />

          {message && (
            <StatusBanner
              type={message.type}
              message={message.text}
              onDismiss={() => setMessage(null)}
            />
          )}

          {}
          <div style={ {
            padding: 32,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            <form className="ui-form"  onSubmit={handleSubmit}>
              {}
              <div style={{ borderBottom: '1px solid #F0F0F0', paddingBottom: 24, marginBottom: 24 }}>
                <div style={ {
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 16
                }}>
                  <h2 style={ {
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    color: 'var(--color-black)',
                    margin: 0,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12
                  }}>
                    <FontAwesomeIcon icon={faMap} style={{ color: 'var(--color-medium-gray)' }} />
                    Select Destination
                  </h2>
                  <button
                    type="button"
                    onClick={() => setShowMap(!showMap)}
                    className="ui-button ui-button-sm ui-button-outline"
                  >
                    {showMap ? 'Hide Map' : 'Show Map'}
                  </button>
                </div>

                {showMap && (
                  <MapPicker
                    value={mapValue}
                    onChange={handleMapChange}
                    placeholder="Search for your destination..."
                    height="280px"
                  />
                )}
              </div>

              {}
              <div style={ {
                borderBottom: '1px solid #F0F0F0'
              }}>
                <h2 style={ {
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 20,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <FontAwesomeIcon icon={faPlane} style={{ color: 'var(--color-medium-gray)' }} />
                  Basic Information
                </h2>

                <div className="ui-row">
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Trip title *
                    </label>
                    <input
                      className="ui-input"
                      value={form.title}
                      onChange={update('title')}
                      placeholder="e.g. Konstanz road trip"
                      style={ {
                        borderColor: form.title ? '#E5E5E5' : 'var(--color-dark-gray)'
                      }}
                    />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Destination *
                    </label>
                    <input
                      className="ui-input"
                      value={form.destination}
                      onChange={update('destination')}
                      placeholder="City / Country"
                      style={ {
                        borderColor: form.destination ? '#E5E5E5' : 'var(--color-dark-gray)'
                      }}
                    />
                  </div>
                </div>

                <div className="ui-row">
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Start date *
                    </label>
                    <input
                      className="ui-input"
                      type="date"
                      value={form.start_date}
                      onChange={update('start_date')}
                      style={ {
                        borderColor: form.start_date ? '#E5E5E5' : 'var(--color-dark-gray)'
                      }}
                    />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      End date
                    </label>
                    <input
                      className="ui-input"
                      type="date"
                      value={form.end_date}
                      onChange={update('end_date')}
                      min={form.start_date}
                    />
                  </div>
                </div>
              </div>

              {}
              <div style={ {
                marginBottom: 32
              }}>
                <h2 style={ {
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 20,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <FontAwesomeIcon icon={faPlane} style={{ color: 'var(--color-medium-gray)' }} />
                  Trip Description
                </h2>

                <div>
                  <label className="ui-label">
                    Short description *
                    <span style={ {
                      color: form.short_description.length > 80 ? 'var(--color-dark-gray)' : 'var(--color-light-gray)',
                      fontWeight: 600,
                      marginLeft: 8
                    }}>
                      ({form.short_description.length}/80)
                    </span>
                  </label>
                  <input
                    className="ui-input"
                    value={form.short_description}
                    onChange={update('short_description')}
                    placeholder="A brief summary of your trip"
                    maxLength={90}
                    style={ {
                      borderColor: form.short_description.length > 80 ? 'var(--color-dark-gray)' : '#E5E5E5'
                    }}
                  />
                  {form.short_description.length > 80 && (
                    <small style={ {
                      color: 'var(--color-black)',
                      fontSize: '0.85rem',
                      display: 'block',
                      marginTop: 4
                    }}>
                      Please keep it under 80 characters
                    </small>
                  )}
                </div>

                <div>
                  <label className="ui-label">Detailed description</label>
                  <textarea
                    className="ui-textarea"
                    value={form.detail_description}
                    onChange={update('detail_description')}
                    placeholder="Tell us more about your planned adventure..."
                    rows={6}
                  />
                </div>
              </div>

              {}
              <div style={ {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 16
              }}>
                <div style={ {
                  color: 'var(--color-light-gray)',
                  fontSize: '0.9rem'
                }}>
                  * Required fields
                </div>

                <div style={{ display: 'flex', gap: 12 }}>
                  <button
                    className="ui-button ui-button-outline"
                    type="button"
                    onClick={() => setForm( {
                      title: '',
                      destination: '',
                      start_date: '',
                      end_date: '',
                      short_description: '',
                      detail_description: '',
                      latitude: '',
                      longitude: '',
                      address: '',
                      country_code: ''
                    })}
                    disabled={loading}
                  >
                    Clear Form
                  </button>
                  <button
                    className="ui-button"
                    type="submit"
                    disabled={loading}
                    style={ {
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 8
                    }}
                  >
                    <FontAwesomeIcon icon={faSave} />
                    {loading ? 'Creating...' : 'Save Itinerary'}
                  </button>
                </div>
              </div>

              {message && (
                <div style={ {
                  marginTop: 16,
                  padding: 16,
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: '#F9F9F9',
                  border: '1px solid #E5E5E5',
                  color: 'var(--color-black)',
                  fontWeight: 500
                }}>
                  {message.text}
                </div>
              )}
            </form>
          </div>
        </div>
      </div>

      {}
      {showWarningModal && createPortal(
        <div style={ {
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000,
          padding: 20
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            setShowWarningModal(false);
            setTravelWarnings([]);
          }
        }}
        >
          <div style={ {
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            maxWidth: 600,
            width: '100%',
            maxHeight: '80vh',
            overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            position: 'relative'
          }}
          onClick={(e) => e.stopPropagation()}
          >
            {}
            <div style={ {
              padding: '24px 32px',
              borderBottom: '1px solid #F0F0F0',
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              backgroundColor: '#FFF4E6'
            }}>
              <FontAwesomeIcon
                icon={faExclamationTriangle}
                style={ {
                  color: '#FF6B00',
                  fontSize: '2rem'
                }}
              />
              <div>
                <h2 style={ {
                  margin: 0,
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--color-black)'
                }}>
                  Travel Safety Warning
                </h2>
                <p style={ {
                  margin: '4px 0 0 0',
                  fontSize: '0.9rem',
                  color: 'var(--color-medium-gray)'
                }}>
                  Important information about your destination
                </p>
              </div>
            </div>

            {}
            <div style={{ padding: '24px 32px' }}>
              <p style={ {
                fontSize: '1rem',
                color: 'var(--color-black)',
                marginBottom: 20,
                lineHeight: 1.6
              }}>
                There {travelWarnings.length === 1 ? 'is a severe travel alert' : 'are severe travel alerts'} for your selected destination. Please review the following warning{travelWarnings.length > 1 ? 's' : ''} carefully:
              </p>

              {travelWarnings.map((warning, index) => (
                <div key={warning.id || index} style={ {
                  backgroundColor: '#FFF4E6',
                  border: '2px solid #FF6B00',
                  borderRadius: 'var(--radius-md)',
                  padding: 16,
                  marginBottom: travelWarnings.length > 1 && index < travelWarnings.length - 1 ? 16 : 0
                }}>
                  <div style={ {
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    marginBottom: 8
                  }}>
                    <span style={ {
                      backgroundColor: '#FF6B00',
                      color: '#FFFFFF',
                      padding: '4px 12px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      textTransform: 'uppercase'
                    }}>
                      {warning.severity}
                    </span>
                    <span style={ {
                      color: 'var(--color-medium-gray)',
                      fontSize: '0.85rem',
                      fontWeight: 600
                    }}>
                      {warning.category}
                    </span>
                  </div>
                  <h3 style={ {
                    margin: '8px 0',
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    color: 'var(--color-black)'
                  }}>
                    {warning.title}
                  </h3>
                  <p style={ {
                    margin: 0,
                    fontSize: '0.95rem',
                    color: 'var(--color-black)',
                    lineHeight: 1.5
                  }}>
                    {warning.description}
                  </p>
                </div>
              ))}

              <div style={ {
                marginTop: 24,
                padding: 16,
                backgroundColor: '#F9F9F9',
                borderRadius: 'var(--radius-md)',
                border: '1px solid #E5E5E5'
              }}>
                <p style={ {
                  margin: 0,
                  fontSize: '0.9rem',
                  color: 'var(--color-black)',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}>
                  <FontAwesomeIcon icon={faExclamationTriangle} style={{ color: '#FF6B00' }} />
                  Please ensure you:
                </p>
                <ul style={ {
                  margin: '8px 0 0 0',
                  paddingLeft: 20,
                  color: 'var(--color-black)',
                  fontSize: '0.9rem'
                }}>
                  <li>Check your government's travel advisories</li>
                  <li>Review your travel insurance coverage</li>
                  <li>Register with your embassy if traveling</li>
                  <li>Stay informed about local conditions</li>
                </ul>
              </div>
            </div>

            {}
            <div style={ {
              padding: '20px 32px',
              borderTop: '1px solid #F0F0F0',
              display: 'flex',
              gap: 12,
              justifyContent: 'flex-end'
            }}>
              <button
                className="ui-button ui-button-outline"
                onClick={() => {
                  setShowWarningModal(false);
                  setTravelWarnings([]);
                }}
                disabled={loading}
              >
                Cancel Trip
              </button>
              <button
                className="ui-button"
                onClick={() => {
                  setShowWarningModal(false);
                  submitItinerary();
                }}
                disabled={loading}
                style={ {
                  backgroundColor: '#FF6B00',
                  borderColor: '#FF6B00'
                }}
              >
                I Understand, Continue Anyway
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}

export default CreateItinerary;
