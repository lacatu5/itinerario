import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faCalendarAlt, faSearch } from '@fortawesome/free-solid-svg-icons';
import '../../styles/itinerary-ui.css';
import '../../styles/ui.css';
import { searchItineraries } from '../../services/itineraries';
import { Link } from 'react-router-dom';
import { PageHeader, EmptyState, StatusBanner } from '../../components/ui';

function SearchTrips() {
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 12;

  async function handleSubmit(e) {
    e.preventDefault();
    await fetchPage(0);
  }

  async function fetchPage(pageIndex) {
    setLoading(true);
    setError(null);
    try {
      const data = await searchItineraries({
        destination,
        startDate,
        endDate,
        searchText,
        page: pageIndex + 1,
        size: pageSize
      });
      if (data && data.results) {
        setResults(Array.isArray(data.results) ? data.results : []);
        setTotalCount(data.total || 0);
      } else if (data && data.items) {
        setResults(Array.isArray(data.items) ? data.items : []);
        setTotalCount(data.total || 0);
      } else {
        setResults(Array.isArray(data) ? data : []);
        setTotalCount(Array.isArray(data) ? data.length : 0);
      }
      setPage(pageIndex);
    } catch (err) {
      setError(err?.message || 'Failed to search');
      setResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          <PageHeader
            title="Search Itineraries"
            subtitle="Find itineraries created by other travellers."
          />

          {}
          <div className="panel section">
            <h2 className="row items-center gap-2" style={ {
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'var(--color-black)'
            }}>
              <FontAwesomeIcon icon={faSearch} style={{ color: 'var(--color-medium-gray)' }} />
              Search Filters
            </h2>

            <form onSubmit={handleSubmit}>
              <div className="col gap-2" style={{ marginBottom: 24 }}>
                <div className="row gap-2" style={{ flexWrap: 'wrap' }}>
                  <div style={{ flex: 1, minWidth: 240 }}>
                  <label style={ {
                    display: 'block',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8,
                    fontSize: '0.95rem'
                  }}>
                    <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 8, color: 'var(--color-medium-gray)' }} />
                    Destination
                  </label>
                  <input
                    type="text"
                    className="ui-input"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    placeholder="e.g., Paris, Tokyo"
                    style={ {
                      width: '100%',
                      padding: '12px 16px',
                      border: '1px solid #E5E5E5',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem'
                    }}
                  />
                  </div>
                  <div style={{ flex: 1, minWidth: 200 }}>
                  <label style={ {
                    display: 'block',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8,
                    fontSize: '0.95rem'
                  }}>
                    <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 8, color: 'var(--color-medium-gray)' }} />
                    Start Date
                  </label>
                  <input
                    type="date"
                    className="ui-input"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    style={ {
                      width: '100%',
                      padding: '12px 16px',
                      border: '1px solid #E5E5E5',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem'
                    }}
                  />
                  </div>
                  <div style={{ flex: 1, minWidth: 200 }}>
                  <label style={ {
                    display: 'block',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8,
                    fontSize: '0.95rem'
                  }}>
                    <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 8, color: 'var(--color-medium-gray)' }} />
                    End Date
                  </label>
                  <input
                    type="date"
                    className="ui-input"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    min={startDate}
                    style={ {
                      width: '100%',
                      padding: '12px 16px',
                      border: '1px solid #E5E5E5',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem'
                    }}
                  />
                  </div>
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={ {
                    display: 'block',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8,
                    fontSize: '0.95rem'
                  }}>
                    Keywords
                  </label>
                  <input
                    type="text"
                    className="ui-input"
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    placeholder="Title or description"
                    style={ {
                      width: '100%',
                      padding: '12px 16px',
                      border: '1px solid #E5E5E5',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem'
                    }}
                  />
                  <div className="text-muted" style={{ fontSize: '0.85rem', marginTop: 6 }}>
                    Combine filters as you like. Leave empty to see all.
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="ui-button"
                style={ {
                  padding: '14px 28px',
                  marginTop: '1.5rem'
                }}
              >
                {loading ? 'Searching...' : 'Search Itineraries'}
              </button>
            </form>
          </div>

          {}
          {error && (
            <StatusBanner type="error" message={error} />
          )}

          {}
          <div className="section">
            {loading ? (
              <div className="panel row justify-center items-center section">
                <p className="text-muted" style={{ margin: 0, fontSize: '0.95rem' }}>
                  Loading results...
                </p>
              </div>
            ) : results.length === 0 ? (
              <EmptyState
                variant="card"
                title="No results found"
                description="Try different filters or broaden your search."
                icon= {
                  <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <circle cx="28" cy="28" r="16" stroke="currentColor" strokeWidth="2"/>
                    <path d="M40 40L52 52" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M22 28H34M28 22V34" stroke="currentColor" strokeWidth="2" strokeLinecap="round" opacity="0.4"/>
                  </svg>
                }
              />
            ) : (
              <div>
                <h2 className="text-black" style={ {
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  marginBottom: 20
                }}>
                  Search Results ({totalCount} itineraries found)
                </h2>
                <div className="grid grid-auto-fit-320 gap-3">
                  {results.map((trip) => (
                    <Link
                      key={trip.id}
                      to={`/itineraries/${trip.id}`}
                      className="panel transition"
                      style={{ textDecoration: 'none' }}
                    >
                      <h3 className="text-black" style={ {
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        marginBottom: 12,
                        lineHeight: 1.3
                      }}>
                        {trip.title}
                      </h3>
                      <div className="row items-center" style={ {
                        marginBottom: 8,
                        color: 'var(--color-medium-gray)',
                        fontSize: '0.9rem',
                        fontWeight: 500
                      }}>
                        <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 8 }} />
                        {trip.destination}
                      </div>
                      <div className="row items-center" style={ {
                        marginBottom: 12,
                        color: 'var(--color-medium-gray)',
                        fontSize: '0.9rem',
                        fontWeight: 500
                      }}>
                        <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 8 }} />
                        {new Date(trip.start_date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </div>
                      {trip.short_description && (
                        <p className="text-muted" style={ {
                          fontSize: '0.85rem',
                          lineHeight: 1.4,
                          margin: 0,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden'
                        }}>
                          {trip.short_description}
                        </p>
                      )}
                    </Link>
                  ))}
                </div>

                {}
                <div className="row justify-between items-center" style={{ marginTop: '1.5rem'}}>
                  <button
                    className="ui-button ui-button-secondary"
                    onClick={() => fetchPage(Math.max(page - 1, 0))}
                    disabled={loading || page === 0}
                    style={{ padding: '10px 18px' }}
                  >
                    Previous
                  </button>
                  <div className="text-muted" style={{ fontSize: '0.95rem' }}>
                    Page {page + 1}
                  </div>
                  <button
                    className="ui-button"
                    onClick={() => fetchPage(page + 1)}
                    disabled={loading || results.length < pageSize}
                    style={{ padding: '10px 18px' }}
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SearchTrips;
