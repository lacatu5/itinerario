import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faCalendarAlt, faUser } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';

function ItineraryCard({ itinerary }) {
  const {
    id,
    title,
    destination,
    start_date,
    end_date,
    short_description,
    image_url,
    owner
  } = itinerary;

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div style={ {
      backgroundColor: '#FFFFFF',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #F0F0F0',
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      transition: 'transform 0.2s ease, box-shadow 0.2s ease'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.08)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
    }}
    >
      {}
      <div style={ {
        height: 160,
        backgroundColor: '#F3F4F6',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {image_url ? (
          <img
            src={image_url}
            alt={title}
            style={ {
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }}
          />
        ) : (
          <div style={ {
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9CA3AF',
            fontSize: '2rem'
          }}>
            <FontAwesomeIcon icon={faMapMarkerAlt} />
          </div>
        )}

        {}
        {owner && (
          <div style={ {
            position: 'absolute',
            bottom: 12,
            left: 12,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            padding: '4px 12px',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: '0.85rem',
            fontWeight: 600,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            {owner.profile_image_url ? (
              <img
                src={owner.profile_image_url}
                alt={owner.name}
                style={ {
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  objectFit: 'cover'
                }}
              />
            ) : (
              <div style={ {
                width: 20,
                height: 20,
                borderRadius: '50%',
                backgroundColor: '#E5E7EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.6rem',
                color: '#6B7280'
              }}>
                <FontAwesomeIcon icon={faUser} />
              </div>
            )}
            <span style={{ color: '#1F2937' }}>{owner.name}</span>
          </div>
        )}
      </div>

      {}
      <div style={{ padding: 20, flex: 1, display: 'flex', flexDirection: 'column' }}>
        <h3 style={ {
          margin: '0 0 8px 0',
          fontSize: '1.1rem',
          fontWeight: 700,
          color: '#111827',
          lineHeight: 1.4
        }}>
          {title}
        </h3>

        <div style={ {
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          color: '#6B7280',
          fontSize: '0.9rem',
          marginBottom: 12
        }}>
          <FontAwesomeIcon icon={faMapMarkerAlt} style={{ width: 14 }} />
          <span>{destination}</span>
        </div>

        <div style={ {
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          color: '#6B7280',
          fontSize: '0.85rem',
          marginBottom: 16
        }}>
          <FontAwesomeIcon icon={faCalendarAlt} style={{ width: 14 }} />
          <span>{formatDate(start_date)} {end_date && `- ${formatDate(end_date)}`}</span>
        </div>

        <p style={ {
          margin: '0 0 20px 0',
          fontSize: '0.95rem',
          color: '#4B5563',
          lineHeight: 1.5,
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          flex: 1
        }}>
          {short_description}
        </p>

        <Link
          to={`/itineraries/${id}`}
          style={ {
            display: 'block',
            textAlign: 'center',
            padding: '10px',
            backgroundColor: '#F3F4F6',
            color: '#374151',
            borderRadius: 'var(--radius-md)',
            textDecoration: 'none',
            fontWeight: 600,
            fontSize: '0.9rem',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#E5E7EB'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#F3F4F6'}
        >
          View Itinerary
        </Link>
      </div>
    </div>
  );
}

export default ItineraryCard;
