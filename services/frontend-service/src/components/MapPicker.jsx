import { useState, useEffect, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faMapMarkerAlt, faTimes, faSpinner } from '@fortawesome/free-solid-svg-icons';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions( {
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const customIcon = new L.Icon( {
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function MapClickHandler({ onLocationSelect }) {
  useMapEvents( {
    click: async (e) => {
      const { lat, lng } = e.latlng;
      onLocationSelect({ lat, lng });
    },
  });
  return null;
}

function FlyToLocation({ position }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.flyTo(position, 13, { duration: 1 });
    }
  }, [position, map]);

  return null;
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}


function MapPicker( {
  value = null,
  onChange,
  placeholder = 'Search for a location...',
  height = '300px',
  initialCenter = [40.416775, -3.703790],
  initialZoom = 5,
  disabled = false
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [marker, setMarker] = useState(value ? [value.lat, value.lng] : null);
  const [address, setAddress] = useState(value?.address || '');
  const [reverseLookupLoading, setReverseLookupLoading] = useState(false);
  const searchRef = useRef(null);

  useEffect(() => {
    if (value && value.lat && value.lng) {
      setMarker([value.lat, value.lng]);
      setAddress(value.address || '');
    }
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchLocations = useCallback(
    debounce(async (query) => {
      if (!query || query.length < 3) {
        setSearchResults([]);
        setShowResults(false);
        return;
      }

      setSearching(true);
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`,
 {
            headers: {
              'Accept-Language': 'en',
            },
          }
        );
        const data = await response.json();
        setSearchResults(data);
        setShowResults(true);
      } catch (error) {
        console.error('Error searching locations:', error);
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 300),
    []
  );

  const reverseGeocode = async (lat, lng) => {
    setReverseLookupLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`,
 {
          headers: {
            'Accept-Language': 'en',
          },
        }
      );
      const data = await response.json();
      return data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    } catch (error) {
      console.error('Error reverse geocoding:', error);
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    } finally {
      setReverseLookupLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    searchLocations(query);
  };

  const handleSelectResult = (result) => {
    const lat = parseFloat(result.lat);
    const lng = parseFloat(result.lon);
    const locationAddress = result.display_name;

    setMarker([lat, lng]);
    setAddress(locationAddress);
    setSearchQuery(locationAddress);
    setShowResults(false);

    if (onChange) {
      onChange( {
        lat,
        lng,
        address: locationAddress,
        name: result.name || locationAddress.split(',')[0],
        country: result.address?.country || '',
        country_code: result.address?.country_code?.toUpperCase() || '',
        region: result.address?.state || result.address?.county || '',
        city: result.address?.city || result.address?.town || result.address?.village || ''
      });
    }
  };

  const handleMapClick = async ({ lat, lng }) => {
    if (disabled) return;

    setMarker([lat, lng]);
    const locationAddress = await reverseGeocode(lat, lng);
    setAddress(locationAddress);
    setSearchQuery(locationAddress);

    if (onChange) {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`,
 {
          headers: {
            'Accept-Language': 'en',
          },
        }
      );
      const data = await response.json();

      onChange( {
        lat,
        lng,
        address: locationAddress,
        name: data.name || data.address?.city || data.address?.town || locationAddress.split(',')[0],
        country: data.address?.country || '',
        country_code: data.address?.country_code?.toUpperCase() || '',
        region: data.address?.state || data.address?.county || '',
        city: data.address?.city || data.address?.town || data.address?.village || ''
      });
    }
  };

  const handleClear = () => {
    setMarker(null);
    setAddress('');
    setSearchQuery('');
    setSearchResults([]);
    if (onChange) {
      onChange(null);
    }
  };

  return (
    <div style={{ width: '100%' }}>
      {}
      <div ref={searchRef} style={{ position: 'relative', marginBottom: 12 }}>
        <div style={{ position: 'relative' }}>
          <FontAwesomeIcon
            icon={searching ? faSpinner : faSearch}
            spin={searching}
            style={ {
              position: 'absolute',
              left: 12,
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--color-medium-gray)',
              fontSize: '0.9rem'
            }}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder={placeholder}
            disabled={disabled}
            className="ui-input"
            style={ {
              paddingLeft: 36,
              paddingRight: marker ? 36 : 12
            }}
          />
          {marker && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              style={ {
                position: 'absolute',
                right: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--color-medium-gray)',
                padding: 4
              }}
            >
              <FontAwesomeIcon icon={faTimes} />
            </button>
          )}
        </div>

        {}
        {showResults && searchResults.length > 0 && (
          <div
            style={ {
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              backgroundColor: '#FFFFFF',
              border: '1px solid #E0E0E0',
              borderRadius: 'var(--radius-md)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              zIndex: 1000,
              maxHeight: 200,
              overflowY: 'auto'
            }}
          >
            {searchResults.map((result, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleSelectResult(result)}
                style={ {
                  width: '100%',
                  padding: '10px 12px',
                  textAlign: 'left',
                  background: 'none',
                  border: 'none',
                  borderBottom: index < searchResults.length - 1 ? '1px solid #F0F0F0' : 'none',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  color: 'var(--color-dark-gray)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 8,
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#F8F9FA'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
              >
                <FontAwesomeIcon
                  icon={faMapMarkerAlt}
                  style={{ color: 'var(--color-primary)', marginTop: 2, flexShrink: 0 }}
                />
                <span style={ {
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {result.display_name}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {}
      <div
        style={ {
          height,
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          border: '1px solid #E0E0E0',
          position: 'relative'
        }}
      >
        <MapContainer
          center={marker || initialCenter}
          zoom={marker ? 13 : initialZoom}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {!disabled && <MapClickHandler onLocationSelect={handleMapClick} />}
          {marker && <FlyToLocation position={marker} />}
          {marker && <Marker position={marker} icon={customIcon} />}
        </MapContainer>

        {}
        {reverseLookupLoading && (
          <div
            style={ {
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(255,255,255,0.9)',
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              color: 'var(--color-medium-gray)',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              zIndex: 1000
            }}
          >
            <FontAwesomeIcon icon={faSpinner} spin />
            Getting address...
          </div>
        )}
      </div>

      {}
      {address && (
        <div
          style={ {
            marginTop: 8,
            padding: '8px 12px',
            backgroundColor: '#F8F9FA',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.85rem',
            color: 'var(--color-dark-gray)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 8
          }}
        >
          <FontAwesomeIcon
            icon={faMapMarkerAlt}
            style={{ color: 'var(--color-primary)', marginTop: 2, flexShrink: 0 }}
          />
          <span style={{ flex: 1 }}>{address}</span>
        </div>
      )}

      {}
      {!marker && !disabled && (
        <p
          style={ {
            marginTop: 8,
            fontSize: '0.8rem',
            color: 'var(--color-medium-gray)',
            margin: '8px 0 0 0'
          }}
        >
          Search for a location or click on the map to select
        </p>
      )}
    </div>
  );
}

export default MapPicker;
