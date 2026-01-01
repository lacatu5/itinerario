import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import '../../styles/itinerary-ui.css';
import {
  getDestination,
  deleteDestination,
  createAdvertisement,
  updateAdvertisement,
  deleteAdvertisement,
  createOffer,
  updateOffer,
  deleteOffer,
  createDiscount,
  updateDiscount,
  deleteDiscount,
  uploadDestinationImage,
  deleteDestinationImage
} from '../../services/destinations';
import { getCurrentUser } from '../../services/authStore';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faMapMarkerAlt,
  faEdit,
  faTrash,
  faPlus,
  faBullhorn,
  faTag,
  faTicketAlt,
  faArrowLeft,
  faCalendarAlt,
  faLink,
  faToggleOn,
  faToggleOff,
  faCamera,
  faImage
} from '@fortawesome/free-solid-svg-icons';
import { resolveImageUrl } from '../../utils/url';

function DestinationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [destination, setDestination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('advertisements');
  const [showForm, setShowForm] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({});
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [isOwner, setIsOwner] = useState(false);
  const [uploadingDestImage, setUploadingDestImage] = useState(false);

  useEffect(() => {
    loadDestination();
  }, [id]);

  const loadDestination = async () => {
    setLoading(true);
    try {
      const data = await getDestination(id);
      setDestination(data);
      const user = getCurrentUser();
      setIsOwner(user && data.owner_email === user.email);
    } catch (e) {
      setDestination(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this destination?')) return;
    try {
      await deleteDestination(id);
      navigate('/destinations');
    } catch (e) {
      alert('Error deleting destination');
    }
  };

  const openForm = (type, item = null) => {
    setShowForm(type);
    setEditingItem(item);
    setImageFile(null);
    setImagePreview(null);
    if (item) {
      setFormData({ ...item });
      if (item.image_url) {
        setImagePreview(resolveImageUrl(item.image_url));
      }
    } else {
      if (type === 'advertisement') {
        setFormData({ title: '', description: '', event_date: '', link_url: '', active: true });
      } else if (type === 'offer') {
        setFormData({ title: '', description: '', accommodation_name: '', price: '', discount_percentage: '', valid_from: '', valid_until: '', link_url: '', active: true });
      } else if (type === 'discount') {
        setFormData({ title: '', description: '', attraction_name: '', discount_percentage: '', valid_from: '', valid_until: '', promo_code: '', link_url: '', active: true });
      }
    }
  };

  const closeForm = () => {
    setShowForm(null);
    setEditingItem(null);
    setFormData({});
    setImageFile(null);
    setImagePreview(null);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('Image must be smaller than 5MB');
      return;
    }

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(editingItem?.image_url ? resolveImageUrl(editingItem.image_url) : null);
  };

  const handleDestinationImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('Image must be smaller than 5MB');
      return;
    }

    setUploadingDestImage(true);
    try {
      await uploadDestinationImage(id, file);
      loadDestination();
    } catch (e) {
      alert('Failed to upload image');
    } finally {
      setUploadingDestImage(false);
    }
  };

  const handleDeleteDestinationImage = async () => {
    if (!window.confirm('Delete this image?')) return;
    try {
      await deleteDestinationImage(id);
      loadDestination();
    } catch (e) {
      alert('Failed to delete image');
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      let createdItem = null;

      if (showForm === 'advertisement') {
        const payload = {
          title: formData.title,
          description: formData.description,
          event_date: formData.event_date || null,
          image_url: editingItem?.image_url || null,
          link_url: formData.link_url || null,
          active: formData.active
        };
        if (editingItem) {
          createdItem = await updateAdvertisement(id, editingItem.id, payload);
        } else {
          createdItem = await createAdvertisement(id, payload);
        }
      } else if (showForm === 'offer') {
        const payload = {
          title: formData.title,
          description: formData.description,
          accommodation_name: formData.accommodation_name,
          price: formData.price ? parseFloat(formData.price) : null,
          discount_percentage: formData.discount_percentage ? parseInt(formData.discount_percentage) : null,
          valid_from: formData.valid_from || null,
          valid_until: formData.valid_until || null,
          image_url: editingItem?.image_url || null,
          link_url: formData.link_url || null,
          active: formData.active
        };
        if (editingItem) {
          createdItem = await updateOffer(id, editingItem.id, payload);
        } else {
          createdItem = await createOffer(id, payload);
        }
      } else if (showForm === 'discount') {
        const payload = {
          title: formData.title,
          description: formData.description,
          attraction_name: formData.attraction_name,
          discount_percentage: parseInt(formData.discount_percentage),
          valid_from: formData.valid_from || null,
          valid_until: formData.valid_until || null,
          promo_code: formData.promo_code || null,
          link_url: formData.link_url || null,
          active: formData.active
        };
        if (editingItem) {
          await updateDiscount(id, editingItem.id, payload);
        } else {
          await createDiscount(id, payload);
        }
      }
      closeForm();
      loadDestination();
    } catch (e) {
      alert('Error saving item');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteItem = async (type, itemId) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    try {
      if (type === 'advertisement') await deleteAdvertisement(id, itemId);
      else if (type === 'offer') await deleteOffer(id, itemId);
      else if (type === 'discount') await deleteDiscount(id, itemId);
      loadDestination();
    } catch (e) {
      alert('Error deleting item');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="ui-page">
        <div className="ui-container">
          <div className="ui-card">
            <div style={{ textAlign: 'center', padding: 60 }}>
              <p className="ui-help">Loading destination...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!destination) {
    return (
      <div className="ui-page">
        <div className="ui-container">
          <div className="ui-card">
            <div style={{ textAlign: 'center', padding: 60 }}>
              <p className="ui-help">Destination not found</p>
              <Link to="/destinations" className="ui-button" style={{ marginTop: 16 }}>
                Back to Destinations
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { key: 'advertisements', label: 'Events', icon: faBullhorn, count: destination.advertisements?.length || 0 },
    { key: 'offers', label: 'Accommodations', icon: faTag, count: destination.offers?.length || 0 },
    { key: 'discounts', label: 'Attractions', icon: faTicketAlt, count: destination.discounts?.length || 0 }
  ];

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          <div style={{ marginBottom: 24 }}>
            <Link to="/destinations" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--color-medium-gray)', textDecoration: 'none', fontSize: '0.95rem', fontWeight: 500 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
              Back to Destinations
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 24 }}>
              <div style={{ flex: 1 }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-black)', marginBottom: 8, lineHeight: 1.2 }}>
                  {destination.name}
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-medium-gray)', fontSize: '1.1rem', fontWeight: 500 }}>
                  <FontAwesomeIcon icon={faMapMarkerAlt} />
                  {destination.region}, {destination.country}
                </div>
                {destination.description && (
                  <p style={{ color: 'var(--color-light-gray)', fontSize: '1rem', marginTop: 12, maxWidth: 600 }}>
                    {destination.description}
                  </p>
                )}

                {}
                <div style={{ marginTop: 20 }}>
                  {destination.image_url ? (
                    <div style={{ position: 'relative', display: 'inline-block' }}>
                      <img
                        src={resolveImageUrl(destination.image_url)}
                        alt={destination.name}
                        style={ {
                          maxWidth: 300,
                          maxHeight: 200,
                          objectFit: 'cover',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid #E0E0E0'
                        }}
                      />
                      {isOwner && (
                        <button
                          onClick={handleDeleteDestinationImage}
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
                            justifyContent: 'center'
                          }}
                          title="Delete image"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ) : isOwner ? (
                    <div style={ {
                      padding: 20,
                      backgroundColor: '#FAFBFC',
                      borderRadius: 'var(--radius-md)',
                      border: '2px dashed #E0E0E0',
                      textAlign: 'center',
                      maxWidth: 300
                    }}>
                      <FontAwesomeIcon icon={faImage} style={{ fontSize: '1.5rem', color: 'var(--color-medium-gray)', marginBottom: 8 }} />
                      <p style={{ color: 'var(--color-medium-gray)', fontSize: '0.9rem', margin: 0 }}>No image yet</p>
                    </div>
                  ) : null}

                  {isOwner && (
                    <div style={{ marginTop: 12 }}>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleDestinationImageUpload}
                        disabled={uploadingDestImage}
                        style={{ display: 'none' }}
                        id="dest-image-upload"
                      />
                      <label
                        htmlFor="dest-image-upload"
                        style={ {
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 8,
                          padding: '10px 16px',
                          backgroundColor: uploadingDestImage ? '#F8F9FA' : 'var(--color-primary)',
                          color: uploadingDestImage ? 'var(--color-medium-gray)' : 'white',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.85rem',
                          fontWeight: 500,
                          cursor: uploadingDestImage ? 'not-allowed' : 'pointer',
                          transition: 'all 0.2s ease',
                          border: 'none',
                          opacity: uploadingDestImage ? 0.7 : 1,
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                      >
                        <FontAwesomeIcon icon={faCamera} />
                        {uploadingDestImage ? 'Uploading...' : destination.image_url ? 'Change Photo' : 'Add Photo'}
                      </label>
                    </div>
                  )}
                </div>
              </div>
              {isOwner && (
                <div style={{ display: 'flex', gap: 12 }}>
                  <Link to={`/destinations/${id}/edit`} className="ui-button ui-button-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                    <FontAwesomeIcon icon={faEdit} />
                    Edit
                  </Link>
                  <button onClick={handleDelete} className="ui-button ui-button-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--color-black)' }}>
                    <FontAwesomeIcon icon={faTrash} />
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>

          <div style={ {
            display: 'flex',
            gap: 8,
            marginBottom: 24,
            backgroundColor: '#FAFBFC',
            padding: 8,
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #E5E5E5',
            flexWrap: 'wrap'
          }}>
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                style={ {
                  flex: 1,
                  minWidth: 140,
                  padding: '14px 24px',
                  border: 'none',
                  backgroundColor: activeTab === tab.key ? '#FFFFFF' : 'transparent',
                  color: activeTab === tab.key ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activeTab === tab.key ? 700 : 500,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: activeTab === tab.key ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8
                }}
              >
                <FontAwesomeIcon icon={tab.icon} />
                {tab.label}
                {tab.count > 0 && (
                  <span style={ {
                    backgroundColor: '#E5E7EB',
                    color: 'var(--color-black)',
                    borderRadius: '12px',
                    minWidth: 20,
                    height: 20,
                    padding: '0 6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700
                  }}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          <div style={ {
            padding: 24,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0'
          }}>
            {isOwner && (
              <div style={{ marginBottom: 24 }}>
                <button
                  onClick={() => openForm(activeTab === 'advertisements' ? 'advertisement' : activeTab === 'offers' ? 'offer' : 'discount')}
                  className="ui-button"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
                >
                  <FontAwesomeIcon icon={faPlus} />
                  Add {activeTab === 'advertisements' ? 'Event' : activeTab === 'offers' ? 'Offer' : 'Discount'}
                </button>
              </div>
            )}

            {activeTab === 'advertisements' && (
              <div style={{ display: 'grid', gap: 16 }}>
                {destination.advertisements?.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-light-gray)' }}>
                    No event advertisements yet
                  </div>
                ) : (
                  destination.advertisements?.map((ad) => (
                    <div key={ad.id} style={ {
                      padding: 20,
                      backgroundColor: '#FAFBFC',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid #E5E5E5'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-black)', margin: 0 }}>{ad.title}</h4>
                            <FontAwesomeIcon icon={ad.active ? faToggleOn : faToggleOff} style={{ color: ad.active ? 'var(--color-black)' : 'var(--color-light-gray)' }} />
                          </div>
                          <p style={{ color: 'var(--color-medium-gray)', fontSize: '0.95rem', margin: '0 0 8px 0' }}>{ad.description}</p>
                          {ad.image_url && (
                            <div style={{ marginBottom: 12 }}>
                              <img
                                src={resolveImageUrl(ad.image_url)}
                                alt={ad.title}
                                style={ {
                                  maxWidth: 200,
                                  maxHeight: 120,
                                  objectFit: 'cover',
                                  borderRadius: 'var(--radius-md)',
                                  border: '1px solid #E0E0E0'
                                }}
                              />
                            </div>
                          )}
                          {ad.event_date && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>
                              <FontAwesomeIcon icon={faCalendarAlt} />
                              {formatDate(ad.event_date)}
                            </div>
                          )}
                          {ad.link_url && (
                            <a href={ad.link_url} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--color-medium-gray)', fontSize: '0.9rem', marginTop: 8 }}>
                              <FontAwesomeIcon icon={faLink} />
                              View details
                            </a>
                          )}
                        </div>
                        {isOwner && (
                          <div style={{ display: 'flex', gap: 8 }}>
                            <button onClick={() => openForm('advertisement', ad)} className="ui-button ui-button-sm ui-button-outline">
                              <FontAwesomeIcon icon={faEdit} />
                            </button>
                            <button onClick={() => handleDeleteItem('advertisement', ad.id)} className="ui-button ui-button-sm ui-button-outline">
                              <FontAwesomeIcon icon={faTrash} />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'offers' && (
              <div style={{ display: 'grid', gap: 16 }}>
                {destination.offers?.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-light-gray)' }}>
                    No accommodation offers yet
                  </div>
                ) : (
                  destination.offers?.map((offer) => (
                    <div key={offer.id} style={ {
                      padding: 20,
                      backgroundColor: '#FAFBFC',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid #E5E5E5'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-black)', margin: 0 }}>{offer.title}</h4>
                            <FontAwesomeIcon icon={offer.active ? faToggleOn : faToggleOff} style={{ color: offer.active ? 'var(--color-black)' : 'var(--color-light-gray)' }} />
                          </div>
                          <p style={{ color: 'var(--color-medium-gray)', fontSize: '0.95rem', margin: '0 0 8px 0' }}>{offer.description}</p>
                          {offer.image_url && (
                            <div style={{ marginBottom: 12 }}>
                              <img
                                src={resolveImageUrl(offer.image_url)}
                                alt={offer.title}
                                style={ {
                                  maxWidth: 200,
                                  maxHeight: 120,
                                  objectFit: 'cover',
                                  borderRadius: 'var(--radius-md)',
                                  border: '1px solid #E0E0E0'
                                }}
                              />
                            </div>
                          )}
                          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 8 }}>
                            <span style={{ fontWeight: 600, color: 'var(--color-black)' }}>{offer.accommodation_name}</span>
                            {offer.price && <span style={{ color: 'var(--color-medium-gray)' }}>€{offer.price}</span>}
                            {offer.discount_percentage && <span style={{ backgroundColor: '#E5E5E5', padding: '2px 8px', borderRadius: 4, fontSize: '0.85rem', fontWeight: 600 }}>{offer.discount_percentage}% OFF</span>}
                          </div>
                          {(offer.valid_from || offer.valid_until) && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>
                              <FontAwesomeIcon icon={faCalendarAlt} />
                              {formatDate(offer.valid_from)} - {formatDate(offer.valid_until)}
                            </div>
                          )}
                        </div>
                        {isOwner && (
                          <div style={{ display: 'flex', gap: 8 }}>
                            <button onClick={() => openForm('offer', offer)} className="ui-button ui-button-sm ui-button-outline">
                              <FontAwesomeIcon icon={faEdit} />
                            </button>
                            <button onClick={() => handleDeleteItem('offer', offer.id)} className="ui-button ui-button-sm ui-button-outline">
                              <FontAwesomeIcon icon={faTrash} />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'discounts' && (
              <div style={{ display: 'grid', gap: 16 }}>
                {destination.discounts?.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-light-gray)' }}>
                    No attraction discounts yet
                  </div>
                ) : (
                  destination.discounts?.map((discount) => (
                    <div key={discount.id} style={ {
                      padding: 20,
                      backgroundColor: '#FAFBFC',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid #E5E5E5'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-black)', margin: 0 }}>{discount.title}</h4>
                            <FontAwesomeIcon icon={discount.active ? faToggleOn : faToggleOff} style={{ color: discount.active ? 'var(--color-black)' : 'var(--color-light-gray)' }} />
                          </div>
                          <p style={{ color: 'var(--color-medium-gray)', fontSize: '0.95rem', margin: '0 0 8px 0' }}>{discount.description}</p>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 8 }}>
                            <span style={{ fontWeight: 600, color: 'var(--color-black)' }}>{discount.attraction_name}</span>
                            <span style={{ backgroundColor: '#E5E5E5', padding: '2px 8px', borderRadius: 4, fontSize: '0.85rem', fontWeight: 600 }}>{discount.discount_percentage}% OFF</span>
                            {discount.promo_code && <span style={{ fontFamily: 'monospace', backgroundColor: '#F0F0F0', padding: '2px 8px', borderRadius: 4, fontSize: '0.85rem' }}>Code: {discount.promo_code}</span>}
                          </div>
                          {(discount.valid_from || discount.valid_until) && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-light-gray)', fontSize: '0.9rem' }}>
                              <FontAwesomeIcon icon={faCalendarAlt} />
                              {formatDate(discount.valid_from)} - {formatDate(discount.valid_until)}
                            </div>
                          )}
                        </div>
                        {isOwner && (
                          <div style={{ display: 'flex', gap: 8 }}>
                            <button onClick={() => openForm('discount', discount)} className="ui-button ui-button-sm ui-button-outline">
                              <FontAwesomeIcon icon={faEdit} />
                            </button>
                            <button onClick={() => handleDeleteItem('discount', discount.id)} className="ui-button ui-button-sm ui-button-outline">
                              <FontAwesomeIcon icon={faTrash} />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {showForm && (
            <div style={ {
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: 20
            }}>
              <div style={ {
                backgroundColor: '#FFFFFF',
                borderRadius: 'var(--radius-lg)',
                padding: 32,
                maxWidth: 600,
                width: '100%',
                maxHeight: '90vh',
                overflow: 'auto'
              }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 24 }}>
                  {editingItem ? 'Edit' : 'Add'} {showForm === 'advertisement' ? 'Event' : showForm === 'offer' ? 'Offer' : 'Discount'}
                </h2>
                <form onSubmit={handleFormSubmit} className="ui-form">
                  <div>
                    <label className="ui-label">Title *</label>
                    <input className="ui-input" value={formData.title || ''} onChange={(e) => setFormData({ ...formData, title: e.target.value })} required />
                  </div>
                  <div>
                    <label className="ui-label">Description *</label>
                    <textarea className="ui-textarea" value={formData.description || ''} onChange={(e) => setFormData({ ...formData, description: e.target.value })} required rows={3} />
                  </div>

                  {showForm === 'advertisement' && (
                    <>
                      <div>
                        <label className="ui-label">Event Date</label>
                        <input className="ui-input" type="date" value={formData.event_date ? formData.event_date.split('T')[0] : ''} onChange={(e) => setFormData({ ...formData, event_date: e.target.value })} />
                      </div>
                      <div>
                        <label className="ui-label">
                          <FontAwesomeIcon icon={faImage} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                          Event Image
                        </label>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8 }}>
                          <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageChange}
                            style={{ display: 'none' }}
                            id="ad-image-upload"
                          />
                          <label
                            htmlFor="ad-image-upload"
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
                              transition: 'all 0.2s ease'
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
                      <div>
                        <label className="ui-label">Link URL</label>
                        <input className="ui-input" value={formData.link_url || ''} onChange={(e) => setFormData({ ...formData, link_url: e.target.value })} placeholder="https://..." />
                      </div>
                    </>
                  )}

                  {showForm === 'offer' && (
                    <>
                      <div>
                        <label className="ui-label">Accommodation Name *</label>
                        <input className="ui-input" value={formData.accommodation_name || ''} onChange={(e) => setFormData({ ...formData, accommodation_name: e.target.value })} required />
                      </div>
                      <div className="ui-row">
                        <div>
                          <label className="ui-label">Price (€)</label>
                          <input className="ui-input" type="number" step="0.01" value={formData.price || ''} onChange={(e) => setFormData({ ...formData, price: e.target.value })} />
                        </div>
                        <div>
                          <label className="ui-label">Discount %</label>
                          <input className="ui-input" type="number" min="0" max="100" value={formData.discount_percentage || ''} onChange={(e) => setFormData({ ...formData, discount_percentage: e.target.value })} />
                        </div>
                      </div>
                      <div className="ui-row">
                        <div>
                          <label className="ui-label">Valid From</label>
                          <input className="ui-input" type="date" value={formData.valid_from ? formData.valid_from.split('T')[0] : ''} onChange={(e) => setFormData({ ...formData, valid_from: e.target.value })} />
                        </div>
                        <div>
                          <label className="ui-label">Valid Until</label>
                          <input className="ui-input" type="date" value={formData.valid_until ? formData.valid_until.split('T')[0] : ''} onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })} />
                        </div>
                      </div>
                      <div>
                        <label className="ui-label">
                          <FontAwesomeIcon icon={faImage} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                          Offer Image
                        </label>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8 }}>
                          <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageChange}
                            style={{ display: 'none' }}
                            id="offer-image-upload"
                          />
                          <label
                            htmlFor="offer-image-upload"
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
                              transition: 'all 0.2s ease'
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
                      <div>
                        <label className="ui-label">Link URL</label>
                        <input className="ui-input" value={formData.link_url || ''} onChange={(e) => setFormData({ ...formData, link_url: e.target.value })} placeholder="https://..." />
                      </div>
                    </>
                  )}

                  {showForm === 'discount' && (
                    <>
                      <div>
                        <label className="ui-label">Attraction Name *</label>
                        <input className="ui-input" value={formData.attraction_name || ''} onChange={(e) => setFormData({ ...formData, attraction_name: e.target.value })} required />
                      </div>
                      <div className="ui-row">
                        <div>
                          <label className="ui-label">Discount % *</label>
                          <input className="ui-input" type="number" min="0" max="100" value={formData.discount_percentage || ''} onChange={(e) => setFormData({ ...formData, discount_percentage: e.target.value })} required />
                        </div>
                        <div>
                          <label className="ui-label">Promo Code</label>
                          <input className="ui-input" value={formData.promo_code || ''} onChange={(e) => setFormData({ ...formData, promo_code: e.target.value })} placeholder="e.g. SUMMER20" />
                        </div>
                      </div>
                      <div className="ui-row">
                        <div>
                          <label className="ui-label">Valid From</label>
                          <input className="ui-input" type="date" value={formData.valid_from ? formData.valid_from.split('T')[0] : ''} onChange={(e) => setFormData({ ...formData, valid_from: e.target.value })} />
                        </div>
                        <div>
                          <label className="ui-label">Valid Until</label>
                          <input className="ui-input" type="date" value={formData.valid_until ? formData.valid_until.split('T')[0] : ''} onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })} />
                        </div>
                      </div>
                      <div>
                        <label className="ui-label">Link URL</label>
                        <input className="ui-input" value={formData.link_url || ''} onChange={(e) => setFormData({ ...formData, link_url: e.target.value })} placeholder="https://..." />
                      </div>
                    </>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input type="checkbox" checked={formData.active} onChange={(e) => setFormData({ ...formData, active: e.target.checked })} />
                      Active
                    </label>
                  </div>

                  <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 24 }}>
                    <button type="button" onClick={closeForm} className="ui-button ui-button-outline" disabled={submitting}>
                      Cancel
                    </button>
                    <button type="submit" className="ui-button" disabled={submitting}>
                      {submitting ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DestinationDetail;
