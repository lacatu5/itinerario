import { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faCalendarAlt, faPlus, faEdit, faTrash, faCamera, faImage, faMap } from '@fortawesome/free-solid-svg-icons';
import {
  createLocation,
  getItineraryLocations,
  updateLocation,
  deleteLocation,
  uploadLocationImage,
  deleteLocationImage
} from '../services/locations';
import '../styles/itinerary-ui.css';
import { resolveImageUrl } from '../utils/url';
import MapPicker from './MapPicker';

function LocationManager({ itineraryId, canEdit = false, onLocationsChange, itineraryStartDate, itineraryEndDate }) {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);

  useEffect(() => {
    loadLocations();
  }, [itineraryId]);

  const loadLocations = async () => {
    try {
      setLoading(true);
      const data = await getItineraryLocations(itineraryId);
      setLocations(data);
      if (onLocationsChange) {
        onLocationsChange(data);
      }
    } catch (e) {
      setError('Failed to load locations');
    } finally {
      setLoading(false);
    }
  };

  const handleAddLocation = () => {
    setEditingLocation( {
      name: '',
      short_description: '',
      from_date: itineraryStartDate || '',
      to_date: itineraryStartDate || ''
    });
    setShowAddForm(true);
  };

  const handleEditLocation = (location) => {
    setEditingLocation( {
      ...location,
      from_date: location.from_date,
      to_date: location.to_date
    });
    setShowAddForm(true);
  };

  const handleSaveLocation = async (locationData) => {
    try {
      setError('');

      if (!locationData.from_date || !locationData.to_date) {
        alert('Please select both Start Date and End Date.');
        return;
      }

      if (editingLocation.id) {
        const updated = await updateLocation(editingLocation.id, locationData);
        const updatedLocations = locations.map(loc =>
          loc.id === editingLocation.id
            ? { ...updated, images: loc.images }
            : loc
        );
        setLocations(updatedLocations);
        if (onLocationsChange) {
          onLocationsChange(updatedLocations);
        }
      } else {
        const newLocation = await createLocation(itineraryId, locationData);
        const updatedLocations = [...locations, { ...newLocation, images: [] }];
        setLocations(updatedLocations);
        if (onLocationsChange) {
          onLocationsChange(updatedLocations);
        }
      }

      setShowAddForm(false);
      setEditingLocation(null);
    } catch (e) {
      console.error(e);
      const msg = e.response?.data?.detail || e.message || 'Failed to save location';
      setError(typeof msg === 'object' ? JSON.stringify(msg) : msg);
    }
  };

  const handleDeleteLocation = async (locationId) => {
    if (!confirm('Are you sure you want to delete this location?')) {
      return;
    }

    try {
      await deleteLocation(locationId);
      const updatedLocations = locations.filter(loc => loc.id !== locationId);
      setLocations(updatedLocations);
      if (onLocationsChange) {
        onLocationsChange(updatedLocations);
      }
    } catch (e) {
      setError(e.message || 'Failed to delete location');
    }
  };

  const handleImageUpload = async (locationId, file) => {
    try {
      const updatedLocation = await uploadLocationImage(locationId, file);

      setLocations(prev => prev.map(loc =>
        loc.id === locationId ? updatedLocation : loc
      ));

      if (onLocationsChange) {
        const updatedLocations = locations.map(loc =>
          loc.id === locationId ? updatedLocation : loc
        );
        onLocationsChange(updatedLocations);
      }
    } catch (e) {
      setError('Failed to upload image');
    }
  };

  const handleImageDelete = async (locationId) => {
    try {
      await deleteLocationImage(locationId);

      setLocations(prev => prev.map(loc =>
        loc.id === locationId ? { ...loc, image_url: null } : loc
      ));

      if (onLocationsChange) {
        const updatedLocations = locations.map(loc =>
          loc.id === locationId ? { ...loc, image_url: null } : loc
        );
        onLocationsChange(updatedLocations);
      }
    } catch (e) {
      setError('Failed to delete image');
    }
  };

  if (loading) {
    return (
      <div style={ {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
        backgroundColor: '#FAFBFC',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid #F0F0F0'
      }}>
        <p className="ui-help" style={{ margin: 0, fontSize: '0.95rem' }}>Loading locations...</p>
      </div>
    );
  }

  return (
    <div style={ {
      marginBottom: 32,
      padding: 24,
      backgroundColor: '#FFFFFF',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #F0F0F0',
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
    }}>
      <div style={ {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24
      }}>
        <h2 style={ {
          fontSize: '1.5rem',
          fontWeight: 700,
          color: 'var(--color-black)',
          margin: 0
        }}>
          Locations & Places
        </h2>
        {canEdit && (
          <button
            onClick={handleAddLocation}
            className="ui-button ui-button-sm"
            style={ {
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 13,
              padding: '8px 16px',
              fontWeight: 500
            }}
          >
            <FontAwesomeIcon icon={faPlus} />
            Add Location
          </button>
        )}
      </div>

      {error && (
        <div style={ {
          marginBottom: 16,
          padding: 12,
          backgroundColor: '#F9F9F9',
          border: '1px solid #E5E5E5',
          borderRadius: 'var(--radius-md)',
          color: 'var(--color-black)',
          fontSize: '0.9rem'
        }}>
          {error}
        </div>
      )}

      {showAddForm && (
        <LocationForm
          location={editingLocation}
          onSave={handleSaveLocation}
          onCancel={() => {
            setShowAddForm(false);
            setEditingLocation(null);
          }}
          itineraryStartDate={itineraryStartDate}
          itineraryEndDate={itineraryEndDate}
        />
      )}

      {!showAddForm && (locations.length === 0 ? (
        <div style={ {
          padding: 40,
          backgroundColor: '#FAFBFC',
          borderRadius: 'var(--radius-lg)',
          border: '2px dashed #E0E0E0',
          textAlign: 'center',
          color: 'var(--color-medium-gray)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 16, opacity: 0.7 }}>
            <FontAwesomeIcon icon={faMapMarkerAlt} />
          </div>
          <h3 style={ {
            fontWeight: 600,
            fontSize: '1.1rem',
            marginBottom: 8,
            color: 'var(--color-black)'
          }}>
            No locations yet
          </h3>
          <p style={ {
            marginBottom: canEdit ? 20 : 0,
            fontSize: '0.95rem',
            lineHeight: 1.4
          }}>
            {canEdit ? 'Add your first location to this itinerary to get started.' : 'This itinerary has no locations to display.'}
          </p>
          {canEdit && (
            <button
              onClick={handleAddLocation}
              className="ui-button ui-button-sm"
              style={ {
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              <FontAwesomeIcon icon={faPlus} />
              Add First Location
            </button>
          )}
        </div>
      ) : (
        <div style={ {
          display: 'grid',
          gap: 20,
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))'
        }}>
          {locations.map((location) => (
            <LocationCard
              key={location.id}
              location={location}
              canEdit={canEdit}
              onEdit={() => handleEditLocation(location)}
              onDelete={() => handleDeleteLocation(location.id)}
              onImageUpload={(file) => handleImageUpload(location.id, file)}
              onImageDelete={() => handleImageDelete(location.id)}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

function LocationCard({ location, canEdit, onEdit, onDelete, onImageUpload, onImageDelete }) {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setUploadError('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setUploadError('Image must be smaller than 5MB');
      return;
    }

    setUploading(true);
    setUploadError('');

    try {
      await onImageUpload(file);
    } catch (e) {
      setUploadError(e.message || 'Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div style={ {
      backgroundColor: 'white',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #F0F0F0',
      overflow: 'hidden',
      transition: 'all 0.2s ease',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
    }}>
      {}
      <div style={ {
        padding: '20px 24px 16px',
        borderBottom: '1px solid #F5F5F5'
      }}>
        <div style={ {
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 8
        }}>
          <div style={{ flex: 1 }}>
            <h3 style={ {
              fontSize: '1.1rem',
              fontWeight: 600,
              color: 'var(--color-black)',
              margin: 0,
              marginBottom: 4
            }}>
              <FontAwesomeIcon
                icon={faMapMarkerAlt}
                style={ {
                  color: 'var(--color-primary)',
                  marginRight: 8,
                  fontSize: '0.9rem'
                }}
              />
              {location.name}
            </h3>
            <div style={ {
              display: 'flex',
              alignItems: 'center',
              color: 'var(--color-medium-gray)',
              fontSize: '0.85rem',
              fontWeight: 500
            }}>
              <FontAwesomeIcon
                icon={faCalendarAlt}
                style={{ marginRight: 6, fontSize: '0.8rem' }}
              />
              {formatDate(location.from_date)} - {formatDate(location.to_date)}
            </div>
          </div>

          {canEdit && (
            <div style={ {
              display: 'flex',
              gap: 8,
              marginLeft: 16
            }}>
              <button
                onClick={onEdit}
                style={ {
                  padding: '6px 8px',
                  backgroundColor: 'transparent',
                  border: '1px solid #E0E0E0',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--color-medium-gray)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#F8F9FA';
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.color = 'var(--color-primary)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.borderColor = '#E0E0E0';
                  e.target.style.color = 'var(--color-medium-gray)';
                }}
                title="Edit location"
              >
                <FontAwesomeIcon icon={faEdit} />
              </button>
              <button
                onClick={onDelete}
                style={ {
                  padding: '6px 8px',
                  backgroundColor: 'transparent',
                  border: '1px solid #E0E0E0',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--color-medium-gray)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#F8F8F8';
                  e.target.style.borderColor = 'var(--color-medium-gray)';
                  e.target.style.color = 'var(--color-medium-gray)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.borderColor = '#E0E0E0';
                  e.target.style.color = 'var(--color-medium-gray)';
                }}
                title="Delete location"
              >
                <FontAwesomeIcon icon={faTrash} />
              </button>
            </div>
          )}
        </div>

        {location.short_description && (
          <p style={ {
            color: 'var(--color-dark-gray)',
            fontSize: '0.9rem',
            lineHeight: 1.4,
            margin: 0,
            marginTop: 8
          }}>
            {location.short_description}
          </p>
        )}
      </div>

      {}
      <div style={{ padding: '20px 24px' }}>
        {location.image_url && (
          <div style={ {
            marginBottom: canEdit ? 16 : 0
          }}>
            <div
              style={ {
                position: 'relative',
                aspectRatio: '16/9',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
                backgroundColor: '#F8F9FA',
                border: '1px solid #F0F0F0',
                maxWidth: '300px'
              }}
            >
              <img
                src={resolveImageUrl(location.image_url)}
                alt={`${location.name} image`}
                style={ {
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
              {canEdit && (
                <button
                  onClick={onImageDelete}
                  style={ {
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  transition: 'all 0.2s ease'
                }}
                title="Delete image"
              >
                ×
              </button>
              )}
            </div>
          </div>
        )}

        {canEdit && (
           <div style={ {
             display: 'flex',
             alignItems: 'center',
             gap: 12,
             marginTop: location.image_url ? 16 : 0
           }}>
             <input
               type="file"
               accept="image/*"
               onChange={handleFileUpload}
               disabled={uploading}
               style={{ display: 'none' }}
               id={`upload-${location.id}`}
             />
             <label
               htmlFor={`upload-${location.id}`}
               style={ {
                 display: 'inline-flex',
                 alignItems: 'center',
                 gap: 8,
                 padding: '10px 16px',
                 backgroundColor: uploading ? '#F8F9FA' : 'var(--color-primary)',
                 color: uploading ? 'var(--color-medium-gray)' : 'white',
                 borderRadius: 'var(--radius-md)',
                 fontSize: '0.85rem',
                 fontWeight: 500,
                 cursor: uploading ? 'not-allowed' : 'pointer',
                 transition: 'all 0.2s ease',
                 border: 'none',
                 opacity: uploading ? 0.7 : 1,
                 boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
               }}
               title={uploading ? 'Uploading image...' : location.image_url ? 'Replace photo' : 'Add a photo to this location'}
             >
               <FontAwesomeIcon
                 icon={uploading ? faImage : faCamera}
                 style={ {
                   fontSize: '0.9rem',
                   opacity: uploading ? 0.7 : 1
                 }}
               />
               {uploading ? 'Uploading...' : location.image_url ? 'Replace Photo' : 'Add Photo'}
             </label>

             {uploadError && (
               <div style={ {
                 display: 'flex',
                 alignItems: 'center',
                 gap: 6,
                 color: 'var(--color-black)',
                 fontSize: '0.8rem',
                 fontWeight: 500,
                 backgroundColor: '#F9F9F9',
                 padding: '6px 12px',
                 borderRadius: 'var(--radius-sm)',
                 border: '1px solid #E5E5E5'
               }}>
                 <span>!</span>
                 {uploadError}
               </div>
             )}
           </div>
         )}

        {!location.image_url && !canEdit && (
          <div style={ {
            padding: 20,
            textAlign: 'center',
            color: 'var(--color-medium-gray)',
            fontSize: '0.9rem',
            backgroundColor: '#FAFBFC',
            borderRadius: 'var(--radius-md)',
            border: '1px dashed #E0E0E0'
          }}>
            <FontAwesomeIcon
              icon={faImage}
              style={ {
                fontSize: '1.5rem',
                marginBottom: 8,
                opacity: 0.7
              }}
            />
            <p style={{ margin: 0 }}>No photos yet</p>
          </div>
        )}
      </div>
    </div>
  );
}

function LocationForm({ location, onSave, onCancel, itineraryStartDate, itineraryEndDate }) {
  const [formData, setFormData] = useState( {
    name: location?.name || '',
    short_description: location?.short_description || '',
    from_date: location?.from_date || '',
    to_date: location?.to_date || '',
    latitude: location?.latitude || '',
    longitude: location?.longitude || '',
    address: location?.address || ''
  });
  const [saving, setSaving] = useState(false);
  const [showMap, setShowMap] = useState(false);

  const mapValue = formData.latitude && formData.longitude ? {
    lat: parseFloat(formData.latitude),
    lng: parseFloat(formData.longitude),
    address: formData.address
  } : null;

  const handleMapChange = (locationData) => {
    if (locationData) {
      setFormData( {
        ...formData,
        name: formData.name || locationData.name || '',
        latitude: String(locationData.lat),
        longitude: String(locationData.lng),
        address: locationData.address || ''
      });
    } else {
      setFormData( {
        ...formData,
        latitude: '',
        longitude: '',
        address: ''
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (new Date(formData.from_date) > new Date(formData.to_date)) {
      alert('From date must be before to date');
      return;
    }

    if (itineraryStartDate) {
      const itineraryStart = new Date(itineraryStartDate);
      const from = new Date(formData.from_date);
      if (from < itineraryStart) {
        alert('La fecha de inicio de la ubicación debe ser dentro del itinerario');
        return;
      }
    }

    if (itineraryEndDate) {
      const itineraryEnd = new Date(itineraryEndDate);
      const to = new Date(formData.to_date);
      if (to > itineraryEnd) {
        alert('La fecha de fin de la ubicación debe ser dentro del itinerario');
        return;
      }
    }

    setSaving(true);
    try {
      await onSave(formData);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="ui-card" style={ {
      backgroundColor: '#FFFFFF',
      border: '1px solid #F0F0F0',
      borderRadius: 'var(--radius-lg)',
      padding: 16,
      marginTop: 12,
      height: 'auto',
      minHeight: 'auto',
      maxWidth: '100%'
    }}>
      <h2 className="ui-title" style={{ fontSize: '1.25rem', marginBottom: 6 }}>
        {location?.id ? 'Edit Location' : 'Add Location'}
      </h2>
      <p className="ui-subtitle" style={{ marginBottom: 12 }}>Complete the details for this place.</p>

      <form onSubmit={handleSubmit}>
        {}
        <div style={{ marginBottom: 16 }}>
          <div style={ {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 8
          }}>
            <label className="ui-label" style={{ marginBottom: 0 }}>
              <FontAwesomeIcon icon={faMap} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
              Pick Location on Map
            </label>
            <button
              type="button"
              onClick={() => setShowMap(!showMap)}
              className="ui-button ui-button-sm ui-button-outline"
              style={{ fontSize: '0.8rem', padding: '6px 12px' }}
            >
              {showMap ? 'Hide Map' : 'Show Map'}
            </button>
          </div>

          {showMap && (
            <MapPicker
              value={mapValue}
              onChange={handleMapChange}
              placeholder="Search for a location..."
              height="250px"
            />
          )}

          {formData.address && !showMap && (
            <div style={ {
              padding: '8px 12px',
              backgroundColor: '#F8F9FA',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem',
              color: 'var(--color-dark-gray)',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <FontAwesomeIcon icon={faMapMarkerAlt} style={{ color: 'var(--color-primary)' }} />
              {formData.address}
            </div>
          )}
        </div>

        <div style={{ marginBottom: 12 }}>
          <label className="ui-label">Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="ui-input"
            required
            maxLength={200}
          />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label className="ui-label">Description</label>
          <textarea
            value={formData.short_description}
            onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
            className="ui-input"
            rows={3}
            required
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
          <div>
            <label className="ui-label">From Date</label>
            <input
              type="date"
              value={formData.from_date}
              onChange={(e) => setFormData({ ...formData, from_date: e.target.value })}
              className="ui-input"
              required
              min={itineraryStartDate || undefined}
              max={itineraryEndDate || undefined}
            />
          </div>
          <div>
            <label className="ui-label">To Date</label>
            <input
              type="date"
              value={formData.to_date}
              onChange={(e) => setFormData({ ...formData, to_date: e.target.value })}
              className="ui-input"
              required
              min={formData.from_date || itineraryStartDate || undefined}
              max={itineraryEndDate || undefined}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onCancel}
            className="ui-button ui-button-secondary"
            disabled={saving}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="ui-button ui-button-primary"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default LocationManager;
