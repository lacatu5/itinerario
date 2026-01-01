import { useEffect, useState } from 'react';
import '../../styles/itinerary-ui.css';
import { getUserItineraries } from '../../services/itineraries';
import { getCurrentUser } from '../../services/authStore';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faCalendarAlt, faPlus, faRoute, faClock } from '@fortawesome/free-solid-svg-icons';
import { PageHeader, EmptyState, StatsGrid, Button } from '../../components/ui';

function Itineraries() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, upcoming: 0, totalDays: 0 });

  useEffect(() => {
    const user = getCurrentUser();
    if (!user) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const res = await getUserItineraries(user.id);
        const items = res?.items || res || [];
        const onlyMine = items.filter((it) => it.owner_id === user.id);
        setItems(onlyMine);

        const now = new Date();
        const upcoming = onlyMine.filter(it => new Date(it.start_date) >= now).length;
        const totalDays = onlyMine.reduce((acc, it) => {
          if (it.start_date && it.end_date) {
            const start = new Date(it.start_date);
            const end = new Date(it.end_date);
            const diffTime = Math.abs(end - start);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            return acc + diffDays;
          }
          return acc;
        }, 0);

        setStats( {
          total: onlyMine.length,
          upcoming,
          totalDays
        });
      } catch (e) {
        setItems([]);
        setStats({ total: 0, upcoming: 0, totalDays: 0 });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          <PageHeader
            title="My Itineraries"
            subtitle="View and manage your created trips"
            action= {
              items.length > 0 && (
                <Button to="/itineraries/new" icon={<FontAwesomeIcon icon={faPlus} />}>
                  New Trip
                </Button>
              )
            }
          >
            {}
            {!loading && items.length > 0 && (
              <StatsGrid
                stats={[
                  { value: stats.total, label: 'Total Trips' },
                  { value: stats.upcoming, label: 'Upcoming' },
                  { value: stats.totalDays, label: 'Total Days' }
                ]}
              />
            )}
          </PageHeader>

          {}
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
              <p className="ui-help" style={{ margin: 0, fontSize: '1rem' }}>Loading itineraries...</p>
            </div>
          ) : items.length === 0 ? (
            <EmptyState
              variant="card"
              title="No itineraries yet"
              description="You haven't created any itineraries yet. Start planning your next adventure!"
              icon= {
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <path d="M16 48L32 16L48 48" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="32" cy="24" r="4" fill="currentColor" opacity="0.3"/>
                  <circle cx="24" cy="40" r="3" fill="currentColor" opacity="0.3"/>
                  <circle cx="40" cy="40" r="3" fill="currentColor" opacity="0.3"/>
                  <path d="M24 40H40" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="4 4"/>
                </svg>
              }
              action= {
                <Button to="/itineraries/new" icon={<FontAwesomeIcon icon={faPlus} />}>
                  Create Your First Itinerary
                </Button>
              }
            />
          ) : (
            <div className="section" style={ {
              display: 'grid',
              gap: 16
            }}>
              {items.map((it) => (
                <Link
                  key={it.id}
                  to={`/itineraries/${it.id}`}
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
                  <div style={ {
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: 16
                  }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={ {
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 8,
                        lineHeight: 1.3
                      }}>
                        {it.title}
                      </h3>

                      <div style={ {
                        display: 'flex',
                        alignItems: 'center',
                        gap: 20,
                        marginBottom: 8,
                        flexWrap: 'wrap'
                      }}>
                        <div style={ {
                          display: 'flex',
                          alignItems: 'center',
                          color: 'var(--color-medium-gray)',
                          fontSize: '0.95rem',
                          fontWeight: 500
                        }}>
                          <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6 }} />
                          {it.destination}
                        </div>

                        <div style={ {
                          display: 'flex',
                          alignItems: 'center',
                          color: 'var(--color-medium-gray)',
                          fontSize: '0.95rem',
                          fontWeight: 500
                        }}>
                          <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 6 }} />
                          {formatDate(it.start_date)}
                        </div>
                      </div>

                      {it.short_description && (
                        <p style={ {
                          color: 'var(--color-light-gray)',
                          fontSize: '0.95rem',
                          lineHeight: 1.5,
                          margin: 0
                        }}>
                          {it.short_description}
                        </p>
                      )}
                    </div>

                    <div style={ {
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--color-medium-gray)',
                      fontSize: '1.2rem'
                    }}>
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

export default Itineraries;
