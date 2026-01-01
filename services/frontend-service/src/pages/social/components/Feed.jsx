import { useState, useEffect } from 'react';
import { getFeed } from '../../../services/itineraries';
import ItineraryCard from './ItineraryCard';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStream, faSpinner } from '@fortawesome/free-solid-svg-icons';

function Feed({ currentUserId }) {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadFeed = async () => {
      if (!currentUserId) {
        setError('Please log in to view your feed');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError('');

      try {
        const data = await getFeed();
        setFeed(data?.items || data || []);
      } catch (err) {
        console.error('Error loading feed:', err);
        const errorMessage = err?.message || 'Failed to load feed';
        if (err?.status === 403 || err?.status === 401) {
          setError('Authentication required. Please try refreshing the page or logging in again.');
        } else {
          setError(errorMessage);
        }
      } finally {
        setLoading(false);
      }
    };

    loadFeed();
  }, [currentUserId]);

  if (loading) {
    return (
      <div style={ {
        textAlign: 'center',
        padding: 60,
        backgroundColor: '#FAFBFC',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid #E5E5E5'
      }}>
        <FontAwesomeIcon icon={faSpinner} spin style={{ fontSize: '2rem', color: '#9CA3AF', marginBottom: 16 }} />
        <p style={{ color: 'var(--color-medium-gray)' }}>Loading your feed...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={ {
        textAlign: 'center',
        padding: 40,
        backgroundColor: '#FEF2F2',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid #FECACA',
        color: '#B91C1C'
      }}>
        <p>{error}</p>
      </div>
    );
  }

  if (feed.length === 0) {
    return (
      <div style={ {
        textAlign: 'center',
        padding: 80,
        backgroundColor: '#FAFBFC',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid #E5E5E5'
      }}>
        <div style={ {
          width: 80,
          height: 80,
          backgroundColor: '#E5E7EB',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
          fontSize: '2rem',
          color: '#9CA3AF'
        }}>
          <FontAwesomeIcon icon={faStream} />
        </div>
        <p style={ {
          fontSize: '1.2rem',
          fontWeight: 600,
          color: 'var(--color-black)',
          marginBottom: 8
        }}>
          Your feed is empty
        </p>
        <p style={ {
          fontSize: '0.95rem',
          color: 'var(--color-light-gray)'
        }}>
          Follow other travelers to see their itineraries here.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 style={ {
        fontSize: '1.5rem',
        fontWeight: 700,
        color: 'var(--color-black)',
        marginBottom: 24,
        display: 'flex',
        alignItems: 'center',
        gap: 10
      }}>
        <FontAwesomeIcon icon={faStream} />
        Your Feed
      </h2>

      <div style={ {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: 24
      }}>
        {feed.map(itinerary => (
          <ItineraryCard key={itinerary.id} itinerary={itinerary} />
        ))}
      </div>
    </div>
  );
}

export default Feed;
