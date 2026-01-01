import { useState } from 'react';
import '../../styles/itinerary-ui.css';
import { createDestination, uploadDestinationImage } from '../../services/destinations';
import { getCurrentUser } from '../../services/authStore';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGlobe, faMapMarkerAlt, faSave, faCamera, faImage, faMap } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import MapPicker from '../../components/MapPicker';

function CreateDestination() {
  const navigate = useNavigate();
  const [form, setForm] = useState( {
    name: '',
    region: '',
    country: '',
    description: '',
    latitude: '',
    longitude: '',
    address: ''
  });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showMap, setShowMap] = useState(true);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const mapValue = form.latitude && form.longitude ? {
    lat: parseFloat(form.latitude),
    lng: parseFloat(form.longitude),
    address: form.address
  } : null;

  const handleMapChange = (locationData) => {
    if (locationData) {
      setForm( {
        ...form,
        name: form.name || locationData.name || '',
        region: form.region || locationData.region || '',
        country: form.country || locationData.country || '',
        latitude: String(locationData.lat),
        longitude: String(locationData.lng),
        address: locationData.address || ''
      });
    } else {
      setForm( {
        ...form,
        latitude: '',
        longitude: '',
        address: ''
      });
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Please select an image file' });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'Image must be smaller than 5MB' });
      return;
    }

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    const user = getCurrentUser();
    if (!user) {
      setMessage({ type: 'error', text: 'Please sign in to create destinations.' });
      return;
    }
    if (!form.name || !form.region || !form.country) {
      setMessage({ type: 'error', text: 'Name, region and country are required.' });
      return;
    }
    setLoading(true);
    try {
      const created = await createDestination( {
        name: form.name,
        region: form.region,
        country: form.country,
        description: form.description || null,
        image_url: null,
        latitude: form.latitude || null,
        longitude: form.longitude || null,
        address: form.address || null
      });

      if (created && created.id && imageFile) {
        try {
          await uploadDestinationImage(created.id, imageFile);
        } catch (imgErr) {
          console.error('Failed to upload image:', imgErr);
        }
      }

      if (created && created.id) {
        navigate(`/destinations/${created.id}`);
        return;
      }
      setMessage({ type: 'success', text: 'Destination created successfully.' });
      setForm({ name: '', region: '', country: '', description: '', latitude: '', longitude: '', address: '' });
      clearImage();
    } catch (err) {
      setMessage({ type: 'error', text: 'Error creating destination.' });
    } finally {
      setLoading(false);
    }
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 24 }}>
              <div>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-black)', marginBottom: 8, lineHeight: 1.2 }}>
                  Add Destination
                </h1>
                <p style={{ color: 'var(--color-medium-gray)', fontSize: '1.1rem', fontWeight: 500, margin: 0 }}>
                  Register a new travel destination
                </p>
              </div>
            </div>
          </div>

          <div style={ {
            padding: 32,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            <form className="ui-form" onSubmit={handleSubmit}>
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
                    Select Location
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
                    placeholder="Search for a destination..."
                    height="300px"
                  />
                )}

                {form.address && !showMap && (
                  <div style={ {
                    padding: '12px 16px',
                    backgroundColor: '#F8F9FA',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '0.9rem',
                    color: 'var(--color-dark-gray)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8
                  }}>
                    <FontAwesomeIcon icon={faMapMarkerAlt} style={{ color: 'var(--color-primary)' }} />
                    {form.address}
                  </div>
                )}
              </div>

              <div style={{ borderBottom: '1px solid #F0F0F0', paddingBottom: 24, marginBottom: 24 }}>
                <h2 style={ {
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 20,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <FontAwesomeIcon icon={faGlobe} style={{ color: 'var(--color-medium-gray)' }} />
                  Destination Information
                </h2>

                <div className="ui-row">
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Destination name *
                    </label>
                    <input
                      className="ui-input"
                      value={form.name}
                      onChange={update('name')}
                      placeholder="e.g. Costa Brava"
                    />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Region *
                    </label>
                    <input
                      className="ui-input"
                      value={form.region}
                      onChange={update('region')}
                      placeholder="e.g. Catalonia"
                    />
                  </div>
                </div>

                <div className="ui-row">
                  <div>
                    <label className="ui-label">Country *</label>
                    <input
                      className="ui-input"
                      value={form.country}
                      onChange={update('country')}
                      placeholder="e.g. Spain"
                    />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faImage} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Destination Image
                    </label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        style={{ display: 'none' }}
                        id="destination-image-upload"
                      />
                      <label
                        htmlFor="destination-image-upload"
                        style={ {
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 8,
                          padding: '10px 16px',
                          backgroundColor: 'var(--color-primary)',
                          color: 'white',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.85rem',
                          fontWeight: 500,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          border: 'none',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                      >
                        <FontAwesomeIcon icon={faCamera} />
                        {imageFile ? 'Change Photo' : 'Add Photo'}
                      </label>
                      {imageFile && (
                        <button
                          type="button"
                          onClick={clearImage}
                          style={ {
                            padding: '8px 12px',
                            backgroundColor: 'transparent',
                            border: '1px solid #E0E0E0',
                            borderRadius: 'var(--radius-md)',
                            color: 'var(--color-medium-gray)',
                            fontSize: '0.85rem',
                            cursor: 'pointer'
                          }}
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    {imagePreview && (
                      <div style={{ marginTop: 12 }}>
                        <img
                          src={imagePreview}
                          alt="Preview"
                          style={ {
                            maxWidth: 200,
                            maxHeight: 150,
                            objectFit: 'cover',
                            borderRadius: 'var(--radius-md)',
                            border: '1px solid #E0E0E0'
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="ui-label">Description</label>
                  <textarea
                    className="ui-textarea"
                    value={form.description}
                    onChange={update('description')}
                    placeholder="Describe your destination..."
                    rows={4}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
                <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>* Required fields</div>
                <div style={{ display: 'flex', gap: 12 }}>
                  <button
                    className="ui-button ui-button-outline"
                    type="button"
                    onClick={() => {
                      setForm({ name: '', region: '', country: '', description: '', latitude: '', longitude: '', address: '' });
                      clearImage();
                    }}
                    disabled={loading}
                  >
                    Clear Form
                  </button>
                  <button
                    className="ui-button"
                    type="submit"
                    disabled={loading}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
                  >
                    <FontAwesomeIcon icon={faSave} />
                    {loading ? 'Creating...' : 'Save Destination'}
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
    </div>
  );
}

export default CreateDestination;
