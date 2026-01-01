import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faCalendarAlt, faUser, faEdit, faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import '../../styles/itinerary-ui.css';
import { getItinerary } from '../../services/itineraries';
import { getCurrentUser } from '../../services/authStore';
import LocationManager from '../../components/LocationManager';
import TransportManager from '../../components/TransportManager';
import LikesAndComments from '../../components/LikesAndComments';
import { resolveImageUrl } from '../../utils/url';
import { getItineraryStats } from '../../services/likes';

function ItineraryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [locations, setLocations] = useState([]);
  const [likeCount, setLikeCount] = useState(0);

  const currentUser = getCurrentUser();

  useEffect(() => {
    (async () => {
      try {
        const data = await getItinerary(id);
        setItem(data);
      } catch (e) {
        setItem(null);
      } finally { setLoading(false); }
    })();
  }, [id]);

  useEffect(() => {
    (async () => {
      if (!item?.id) return;
      try {
        const stats = await getItineraryStats(item.id);
        setLikeCount(stats?.like_count ?? 0);
      } catch (e) {
        setLikeCount(0);
      }
    })();
  }, [item?.id]);

  const canEdit = currentUser && item && currentUser.id === item.owner_id;

  const handleGoBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate(currentUser ? '/itineraries' : '/search');
    }
  };

  const calculateDuration = () => {
    if (!item?.start_date || !item?.end_date) return null;
    const start = new Date(item.start_date);
    const end = new Date(item.end_date);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          {loading ? (
            <div style={ {
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              padding: 40,
              backgroundColor: '#FAFBFC',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid #F0F0F0'
            }}>
              <p className="ui-help" style={{ margin: 0, fontSize: '0.95rem' }}>Loading itinerary...</p>
            </div>
          ) : !item ? (
            <div className="ui-empty">
              <p className="ui-empty-title">Itinerary not found</p>
              <p className="ui-empty-sub">Check the link or go back to the list.</p>
              <button
                onClick={handleGoBack}
                className="ui-button ui-button-sm"
                style={ {
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8
                }}
              >
                <FontAwesomeIcon icon={faArrowLeft} />
                Go Back
              </button>
            </div>
          ) : (
            <>
              {}
              <div style={ {
                marginBottom: 32,
                padding: 32,
                backgroundColor: '#FFFFFF',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid #F0F0F0',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
              }}>
                {}
                <div style={ {
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 16
                }}>
                  <button
                    onClick={handleGoBack}
                    className="ui-button ui-button-secondary"
                    style={ {
                      fontSize: 13,
                      padding: '8px 16px',
                      fontWeight: 500,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 8
                    }}
                  >
                    <FontAwesomeIcon icon={faArrowLeft} />
                    Go Back
                  </button>
                  {canEdit && (
                    <Link
                      to={`/itineraries/${item.id}/edit`}
                      className="ui-button ui-button-outline ui-button-sm"
                      style={{ fontSize: 12, padding: '6px 12px' }}
                    >
                      <FontAwesomeIcon icon={faEdit} style={{ marginRight: 6 }} />
                      Edit
                    </Link>
                  )}
                </div>
                {}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={ {
                    display: 'flex',
                    justifyContent: 'flex-start',
                    alignItems: 'flex-start',
                    gap: 16
                  }}>
                    <h1 style={ {
                      fontSize: '2.5rem',
                      fontWeight: 700,
                      color: 'var(--color-black)',
                      marginBottom: 12,
                      lineHeight: 1.2
                    }}>
                      {item.title}
                    </h1>
                  </div>

                  <div style={ {
                    display: 'flex',
                    alignItems: 'center',
                    gap: 24,
                    marginBottom: 16,
                    flexWrap: 'wrap'
                  }}>
                    <div style={ {
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--color-medium-gray)',
                      fontSize: '1.1rem',
                      fontWeight: 500
                    }}>
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 8, color: 'var(--color-medium-gray)' }} />
                      {item.destination}
                    </div>

                    <div style={ {
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--color-medium-gray)',
                      fontSize: '1.1rem',
                      fontWeight: 500
                    }}>
                      <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 8, color: 'var(--color-medium-gray)' }} />
                      {new Date(item.start_date).toLocaleDateString()}
                      {item.end_date && ` - ${new Date(item.end_date).toLocaleDateString()}`}
                    </div>
                  </div>

                  {item.short_description && (
                    <p style={ {
                      color: 'var(--color-light-gray)',
                      fontSize: '1.1rem',
                      marginBottom: 20,
                      lineHeight: 1.5,
                      fontStyle: 'italic'
                    }}>
                      {item.short_description}
                    </p>
                  )}

                  {}
                  <div style={ {
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                    gap: 24,
                    marginTop: 20
                  }}>
                    <div>
                      <div style={ {
                        fontSize: '1.75rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 4
                      }}>
                        {locations.length || 0}
                      </div>
                      <div style={ {
                        color: 'var(--color-light-gray)',
                        fontSize: '1rem',
                        fontWeight: 500
                      }}>
                        Locations
                      </div>
                    </div>
                    <div>
                      <div style={ {
                        fontSize: '1.75rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 4
                      }}>
                        {likeCount}
                      </div>
                      <div style={ {
                        color: 'var(--color-light-gray)',
                        fontSize: '1rem',
                        fontWeight: 500
                      }}>
                        Likes
                      </div>
                    </div>
                    {calculateDuration() && (
                      <div>
                        <div style={ {
                          fontSize: '1.75rem',
                          fontWeight: 700,
                          color: 'var(--color-black)',
                          marginBottom: 4
                        }}>
                          {calculateDuration()}
                        </div>
                        <div style={ {
                          color: 'var(--color-light-gray)',
                          fontSize: '1rem',
                          fontWeight: 500
                        }}>
                          Days
                        </div>
                      </div>
                    )}
                    <div>
                      <div style={ {
                        fontSize: '1.75rem',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: 4
                      }}>
                        {new Date(item.created_at).getFullYear()}
                      </div>
                      <div style={ {
                        color: 'var(--color-light-gray)',
                        fontSize: '1rem',
                        fontWeight: 500
                      }}>
                        Created
                      </div>
                    </div>
                  </div>

                  {}
                  {item.owner && (
                    <div style={ {
                      marginTop: 24,
                      padding: 16,
                      backgroundColor: '#FAFBFC',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid #F0F0F0'
                    }}>
                      <div style={ {
                        display: 'flex',
                        alignItems: 'center',
                        gap: 12
                      }}>
                        {item.owner.profile_image_url ? (
                          <img
                            src={resolveImageUrl(item.owner.profile_image_url)}
                            alt="Owner"
                            style={ {
                              width: 40,
                              height: 40,
                              objectFit: 'cover',
                              borderRadius: '50%',
                              border: '2px solid #F8F9FA'
                            }}
                          />
                        ) : (
                          <div style={ {
                            width: 40,
                            height: 40,
                            backgroundColor: '#E5E7EB',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 14,
                            fontWeight: 600,
                            color: '#6B7280'
                          }}>
                            {getInitials(item.owner.name)}
                          </div>
                        )}
                        <div>
                          <div style={ {
                            fontSize: '1rem',
                            fontWeight: 600,
                            color: 'var(--color-black)',
                            marginBottom: 2
                          }}>
                            {item.owner.name}
                          </div>
                          <div style={ {
                            fontSize: '0.9rem',
                            color: 'var(--color-medium-gray)'
                          }}>
                            Trip Creator
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {}
              {item.detail_description && (
                <div style={ {
                  marginBottom: 32,
                  padding: 24,
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #F0F0F0',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                }}>
                  <h2 style={ {
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    color: 'var(--color-black)',
                    marginBottom: 16
                  }}>
                    About This Trip
                  </h2>
                  <div style={ {
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                    color: 'var(--color-medium-gray)',
                    fontSize: '1rem'
                  }}>
                    {item.detail_description}
                  </div>
                </div>
              )}

              {}
              <TransportManager
                itineraryId={item.id}
                canEdit={canEdit}
              />

              {}
              <LocationManager
                itineraryId={item.id}
                canEdit={canEdit}
                itineraryStartDate={item.start_date}
                itineraryEndDate={item.end_date}
                onLocationsChange={setLocations}
              />

              {}
              <LikesAndComments
                itineraryId={item.id}
                ownerId={item.owner_id}
                onStatsChange={(count) => setLikeCount(count)}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default ItineraryDetail;
