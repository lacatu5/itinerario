import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import '../../styles/itinerary-ui.css';
import { getDestination, updateDestination, uploadDestinationImage, deleteDestinationImage } from '../../services/destinations';
import { getCurrentUser } from '../../services/authStore';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGlobe, faMapMarkerAlt, faSave, faArrowLeft, faCamera, faImage, faMap } from '@fortawesome/free-solid-svg-icons';
import { resolveImageUrl } from '../../utils/url';
import MapPicker from '../../components/MapPicker';

function EditDestination() {
  const { id } = useParams();
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
  const [currentImageUrl, setCurrentImageUrl] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showMap, setShowMap] = useState(false);

  useEffect(() => {
    loadDestination();
  }, [id]);

  const loadDestination = async () => {
    try {
      const data = await getDestination(id);
      const user = getCurrentUser();
      if (!user || data.owner_email !== user.email) {
        navigate('/destinations');
        return;
      }
      setForm( {
        name: data.name || '',
        region: data.region || '',
        country: data.country || '',
        description: data.description || '',
        latitude: data.latitude || '',
        longitude: data.longitude || '',
        address: data.address || ''
      });
      setCurrentImageUrl(data.image_url);
      if (data.image_url) {
        setImagePreview(resolveImageUrl(data.image_url));
      }
      if (data.latitude && data.longitude) {
        setShowMap(true);
      }
    } catch (e) {
      navigate('/destinations');
    } finally {
      setLoading(false);
    }
  };

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
    setImagePreview(currentImageUrl ? resolveImageUrl(currentImageUrl) : null);
  };

  const handleDeleteImage = async () => {
    if (!window.confirm('Delete this image?')) return;
    try {
      await deleteDestinationImage(id);
      setCurrentImageUrl(null);
      setImagePreview(null);
      setImageFile(null);
    } catch (e) {
      setMessage({ type: 'error', text: 'Failed to delete image' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    if (!form.name || !form.region || !form.country) {
      setMessage({ type: 'error', text: 'Name, region and country are required.' });
      return;
    }
    setSubmitting(true);
    try {
      await updateDestination(id, {
        name: form.name,
        region: form.region,
        country: form.country,
        description: form.description || null,
        latitude: form.latitude || null,
        longitude: form.longitude || null,
        address: form.address || null
      });

      if (imageFile) {
        try {
          await uploadDestinationImage(id, imageFile);
        } catch (imgErr) {
          console.error('Failed to upload image:', imgErr);
        }
      }

      navigate(`/destinations/${id}`);
    } catch (err) {
      setMessage({ type: 'error', text: 'Error updating destination.' });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="ui-page">
        <div className="ui-container">
          <div className="ui-card">
            <div style={{ textAlign: 'center', padding: 60 }}>
              <p className="ui-help">Loading...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          <div style={{ marginBottom: 24 }}>
            <Link to={`/destinations/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--color-medium-gray)', textDecoration: 'none', fontSize: '0.95rem', fontWeight: 500 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
              Back to Destination
            </Link>
          </div>

          <div style={ {
            marginBottom: 32,
            padding: 32,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-black)', marginBottom: 8, lineHeight: 1.2 }}>
              Edit Destination
            </h1>
            <p style={{ color: 'var(--color-medium-gray)', fontSize: '1.1rem', fontWeight: 500, margin: 0 }}>
              Update destination details
            </p>
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
                    Location on Map
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
                    <input className="ui-input" value={form.name} onChange={update('name')} placeholder="e.g. Costa Brava" />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Region *
                    </label>
                    <input className="ui-input" value={form.region} onChange={update('region')} placeholder="e.g. Catalonia" />
                  </div>
                </div>

                <div className="ui-row">
                  <div>
                    <label className="ui-label">Country *</label>
                    <input className="ui-input" value={form.country} onChange={update('country')} placeholder="e.g. Spain" />
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
                        id="edit-destination-image-upload"
                      />
                      <label
                        htmlFor="edit-destination-image-upload"
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
                        {imageFile ? 'Change Photo' : imagePreview ? 'Replace Photo' : 'Add Photo'}
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
                          Cancel
                        </button>
                      )}
                      {currentImageUrl && !imageFile && (
                        <button
                          type="button"
                          onClick={handleDeleteImage}
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
                  <textarea className="ui-textarea" value={form.description} onChange={update('description')} placeholder="Describe your destination..." rows={4} />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
                <div style={{ color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>* Required fields</div>
                <div style={{ display: 'flex', gap: 12 }}>
                  <Link to={`/destinations/${id}`} className="ui-button ui-button-outline">
                    Cancel
                  </Link>
                  <button className="ui-button" type="submit" disabled={submitting} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                    <FontAwesomeIcon icon={faSave} />
                    {submitting ? 'Saving...' : 'Save Changes'}
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

export default EditDestination;
