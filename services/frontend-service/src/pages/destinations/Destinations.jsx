import { useEffect, useState } from 'react';
import '../../styles/itinerary-ui.css';
import { getDestinations } from '../../services/destinations';
import { getCurrentUser } from '../../services/authStore';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faPlus, faGlobe, faBullhorn, faTag, faTicketAlt } from '@fortawesome/free-solid-svg-icons';

function Destinations() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, ads: 0, offers: 0, discounts: 0 });

  useEffect(() => {
    const user = getCurrentUser();
    if (!user) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const allDestinations = await getDestinations();
        const myDestinations = allDestinations.filter(d => d.owner_id === user.id);
        setItems(myDestinations);
        setStats({
          total: myDestinations.length,
          ads: 0,
          offers: 0,
          discounts: 0
        });
      } catch (e) {
        setItems([]);
        setStats({ total: 0, ads: 0, offers: 0, discounts: 0 });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

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
            <div style={ {
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              flexWrap: 'wrap',
              gap: 24
            }}>
              <div>
                <h1 style={ {
                  fontSize: '2.5rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 8,
                  lineHeight: 1.2
                }}>
                  My Destinations
                </h1>
                <p style={ {
                  color: 'var(--color-medium-gray)',
                  fontSize: '1.1rem',
                  fontWeight: 500,
                  margin: 0
                }}>
                  Manage your travel destinations and promotions
                </p>
              </div>
              <Link
                to="/destinations/new"
                className="ui-button"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <FontAwesomeIcon icon={faPlus} />
                Add Destination
              </Link>
            </div>

            {!loading && items.length > 0 && (
              <div style={ {
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: 24,
                marginTop: 24,
                paddingTop: 24,
                borderTop: '1px solid #F0F0F0'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-black)', marginBottom: 4 }}>
                    {stats.total}
                  </div>
                  <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem', fontWeight: 500 }}>
                    Destinations
                  </div>
                </div>
              </div>
            )}
          </div>

          {loading ? (
            <div className="section" style={ {
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              padding: 60,
              backgroundColor: '#FAFBFC',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid #F0F0F0'
            }}>
              <p className="ui-help" style={{ margin: 0, fontSize: '1rem' }}>Loading destinations...</p>
            </div>
          ) : items.length === 0 ? (
            <div className="section" style={ {
              textAlign: 'center',
              padding: 64,
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid #F0F0F0',
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
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
                <FontAwesomeIcon icon={faGlobe} />
              </div>
              <h3 style={{ fontWeight: 700, color: 'var(--color-black)', fontSize: '1.5rem', marginBottom: 8 }}>
                No destinations yet
              </h3>
              <p style={ {
                color: 'var(--color-light-gray)',
                fontSize: '1rem',
                marginBottom: 24,
                maxWidth: 400,
                marginLeft: 'auto',
                marginRight: 'auto'
              }}>
                Create your first destination to start promoting events, accommodations, and attractions.
              </p>
              <Link
                to="/destinations/new"
                className="ui-button"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <FontAwesomeIcon icon={faPlus} />
                Add Your First Destination
              </Link>
            </div>
          ) : (
            <div className="section" style={{ display: 'grid', gap: 16 }}>
              {items.map((dest) => (
                <Link
                  key={dest.id}
                  to={`/destinations/${dest.id}`}
                  style={ {
                    display: 'block',
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #F0F0F0',
                    borderRadius: 'var(--radius-lg)',
                    padding: 24,
                    textDecoration: 'none',
                    transition: 'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={ {
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 8,
                        lineHeight: 1.3
                      }}>
                        {dest.name}
                      </h3>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 8, flexWrap: 'wrap' }}>
                        <div style={ {
                          display: 'flex',
                          alignItems: 'center',
                          color: 'var(--color-medium-gray)',
                          fontSize: '0.95rem',
                          fontWeight: 500
                        }}>
                          <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6 }} />
                          {dest.region}, {dest.country}
                        </div>
                      </div>
                      {dest.description && (
                        <p style={ {
                          color: 'var(--color-light-gray)',
                          fontSize: '0.95rem',
                          lineHeight: 1.5,
                          margin: 0
                        }}>
                          {dest.description}
                        </p>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', color: 'var(--color-medium-gray)', fontSize: '1.2rem' }}>
                      →
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Destinations;
