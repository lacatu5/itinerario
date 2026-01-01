import { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPlane,
  faTrain,
  faBus,
  faCar,
  faShip,
  faPlus,
  faEdit,
  faTrash,
  faArrowRight,
  faClock,
  faTicketAlt
} from '@fortawesome/free-solid-svg-icons';
import {
  createTransport,
  getItineraryTransports,
  updateTransport,
  deleteTransport
} from '../services/transports';
import '../styles/itinerary-ui.css';

function TransportManager({ itineraryId, canEdit = false, onTransportsChange }) {
  const [transports, setTransports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTransport, setEditingTransport] = useState(null);

  useEffect(() => {
    loadTransports();
  }, [itineraryId]);

  const loadTransports = async () => {
    try {
      setLoading(true);
      const data = await getItineraryTransports(itineraryId);
      setTransports(data);
      if (onTransportsChange) {
        onTransportsChange(data);
      }
    } catch (e) {
      setError('Failed to load transports');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransport = () => {
    setEditingTransport( {
      type: 'Flight',
      departure_location: '',
      arrival_location: '',
      departure_time: '',
      arrival_time: '',
      carrier: '',
      transport_number: ''
    });
    setShowAddForm(true);
  };

  const handleEditTransport = (transport) => {
    setEditingTransport( {
      ...transport,
      departure_time: transport.departure_time ? transport.departure_time.slice(0, 16) : '',
      arrival_time: transport.arrival_time ? transport.arrival_time.slice(0, 16) : ''
    });
    setShowAddForm(true);
  };

  const handleSaveTransport = async (transportData) => {
    try {
      setError('');

      if (!transportData.departure_time || !transportData.arrival_time) {
        alert('Please select both Departure and Arrival times.');
        return;
      }

      const payload = {
        ...transportData,
        departure_time: new Date(transportData.departure_time).toISOString(),
        arrival_time: new Date(transportData.arrival_time).toISOString()
      };

      if (editingTransport.id) {
        const updated = await updateTransport(editingTransport.id, payload);
        const updatedTransports = transports.map(t =>
          t.id === editingTransport.id ? updated : t
        );
        setTransports(updatedTransports);
        if (onTransportsChange) onTransportsChange(updatedTransports);
      } else {
        const newTransport = await createTransport(itineraryId, payload);
        const updatedTransports = [...transports, newTransport];
        setTransports(updatedTransports);
        if (onTransportsChange) onTransportsChange(updatedTransports);
      }

      setShowAddForm(false);
      setEditingTransport(null);
    } catch (e) {
      console.error(e);
      const msg = e.response?.data?.detail || e.message || 'Failed to save transport';
      setError(typeof msg === 'object' ? JSON.stringify(msg) : msg);
    }
  };

  const handleDeleteTransport = async (transportId) => {
    if (!confirm('Are you sure you want to delete this transport?')) {
      return;
    }

    try {
      await deleteTransport(transportId);
      const updatedTransports = transports.filter(t => t.id !== transportId);
      setTransports(updatedTransports);
      if (onTransportsChange) onTransportsChange(updatedTransports);
    } catch (e) {
      setError(e.message || 'Failed to delete transport');
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
        <p className="ui-help" style={{ margin: 0, fontSize: '0.95rem' }}>Loading transports...</p>
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
          Travel & Transport
        </h2>
        {canEdit && (
          <button
            onClick={handleAddTransport}
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
            Add Transport
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
        <TransportForm
          transport={editingTransport}
          onSave={handleSaveTransport}
          onCancel={() => {
            setShowAddForm(false);
            setEditingTransport(null);
          }}
        />
      )}

      {!showAddForm && (transports.length === 0 ? (
        <div style={ {
          padding: 40,
          backgroundColor: '#FAFBFC',
          borderRadius: 'var(--radius-lg)',
          border: '2px dashed #E0E0E0',
          textAlign: 'center',
          color: 'var(--color-medium-gray)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 16, opacity: 0.7 }}>
            <FontAwesomeIcon icon={faPlane} />
          </div>
          <h3 style={ {
            fontWeight: 600,
            fontSize: '1.1rem',
            marginBottom: 8,
            color: 'var(--color-black)'
          }}>
            No transport details yet
          </h3>
          <p style={ {
            marginBottom: canEdit ? 20 : 0,
            fontSize: '0.95rem',
            lineHeight: 1.4
          }}>
            {canEdit ? 'Add flights, trains, or other transport details.' : 'This itinerary has no transport details.'}
          </p>
          {canEdit && (
            <button
              onClick={handleAddTransport}
              className="ui-button ui-button-sm"
              style={ {
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              <FontAwesomeIcon icon={faPlus} />
              Add Transport
            </button>
          )}
        </div>
      ) : (
        <div style={ {
          display: 'grid',
          gap: 16
        }}>
          {transports.map((transport) => (
            <TransportCard
              key={transport.id}
              transport={transport}
              canEdit={canEdit}
              onEdit={() => handleEditTransport(transport)}
              onDelete={() => handleDeleteTransport(transport.id)}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

function TransportCard({ transport, canEdit, onEdit, onDelete }) {
  const getIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'flight': return faPlane;
      case 'train': return faTrain;
      case 'bus': return faBus;
      case 'car': return faCar;
      case 'ship': return faShip;
      default: return faPlane;
    }
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  return (
    <div style={ {
      backgroundColor: 'white',
      borderRadius: 'var(--radius-md)',
      border: '1px solid #F0F0F0',
      padding: '16px 20px',
      display: 'flex',
      alignItems: 'center',
      gap: 20,
      transition: 'all 0.2s ease',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
    }}>
      {}
      <div style={ {
        width: 48,
        height: 48,
        borderRadius: '50%',
        backgroundColor: '#F0F7FF',
        color: 'var(--color-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '1.2rem',
        flexShrink: 0
      }}>
        <FontAwesomeIcon icon={getIcon(transport.type)} />
      </div>

      {}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={ {
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          marginBottom: 6,
          flexWrap: 'wrap'
        }}>
          <span style={ {
            fontWeight: 600,
            fontSize: '1.05rem',
            color: 'var(--color-black)'
          }}>
            {transport.departure_location}
          </span>
          <FontAwesomeIcon icon={faArrowRight} style={{ color: '#9CA3AF', fontSize: '0.9rem' }} />
          <span style={ {
            fontWeight: 600,
            fontSize: '1.05rem',
            color: 'var(--color-black)'
          }}>
            {transport.arrival_location}
          </span>
        </div>

        <div style={ {
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          color: 'var(--color-medium-gray)',
          fontSize: '0.9rem',
          flexWrap: 'wrap'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <FontAwesomeIcon icon={faClock} style={{ fontSize: '0.85rem' }} />
            {formatDateTime(transport.departure_time)}
          </div>
          {(transport.carrier || transport.transport_number) && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <FontAwesomeIcon icon={faTicketAlt} style={{ fontSize: '0.85rem' }} />
              {transport.carrier} {transport.transport_number}
            </div>
          )}
        </div>
      </div>

      {}
      {canEdit && (
        <div style={ {
          display: 'flex',
          gap: 8,
          marginLeft: 'auto'
        }}>
          <button
            onClick={onEdit}
            style={ {
              padding: '8px',
              backgroundColor: 'transparent',
              border: '1px solid #E0E0E0',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-medium-gray)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            title="Edit"
          >
            <FontAwesomeIcon icon={faEdit} />
          </button>
          <button
            onClick={onDelete}
            style={ {
              padding: '8px',
              backgroundColor: 'transparent',
              border: '1px solid #E0E0E0',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-medium-gray)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            title="Delete"
          >
            <FontAwesomeIcon icon={faTrash} />
          </button>
        </div>
      )}
    </div>
  );
}

function TransportForm({ transport, onSave, onCancel }) {
  const [formData, setFormData] = useState( {
    type: transport?.type || 'Flight',
    departure_location: transport?.departure_location || '',
    arrival_location: transport?.arrival_location || '',
    departure_time: transport?.departure_time || '',
    arrival_time: transport?.arrival_time || '',
    carrier: transport?.carrier || '',
    transport_number: transport?.transport_number || ''
  });
  const [saving, setSaving] = useState(false);

  const TRANSPORT_TYPES = [
    { value: 'Flight', icon: faPlane, label: 'Flight' },
    { value: 'Train', icon: faTrain, label: 'Train' },
    { value: 'Bus', icon: faBus, label: 'Bus' },
    { value: 'Car', icon: faCar, label: 'Car' },
    { value: 'Ship', icon: faShip, label: 'Ship' },
    { value: 'Other', icon: faPlus, label: 'Other' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (new Date(formData.departure_time) > new Date(formData.arrival_time)) {
      alert('Departure time must be before arrival time');
      return;
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
        {transport?.id ? 'Edit Transport' : 'Add Transport'}
      </h2>
      <p className="ui-subtitle" style={{ marginBottom: 12 }}>Enter flight, train, or bus details.</p>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 16 }}>
          <label className="ui-label" style={{ marginBottom: 8, display: 'block' }}>Type</label>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {TRANSPORT_TYPES.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setFormData({ ...formData, type: type.value })}
                style={ {
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  border: '1px solid',
                  borderColor: formData.type === type.value ? 'var(--color-primary)' : '#E5E7EB',
                  backgroundColor: formData.type === type.value ? 'var(--color-primary)' : '#F9FAFB',
                  color: formData.type === type.value ? 'white' : '#6B7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  fontSize: '1.1rem'
                }}
                title={type.label}
              >
                <FontAwesomeIcon icon={type.icon} />
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
          <div>
            <label className="ui-label">Departure Location</label>
            <input
              type="text"
              value={formData.departure_location}
              onChange={(e) => setFormData({ ...formData, departure_location: e.target.value })}
              className="ui-input"
              placeholder="e.g. JFK Airport"
              required
            />
          </div>
          <div>
            <label className="ui-label">Arrival Location</label>
            <input
              type="text"
              value={formData.arrival_location}
              onChange={(e) => setFormData({ ...formData, arrival_location: e.target.value })}
              className="ui-input"
              placeholder="e.g. LHR Airport"
              required
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
          <div>
            <label className="ui-label">Departure Time</label>
            <input
              type="datetime-local"
              value={formData.departure_time}
              onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
              className="ui-input"
              required
            />
          </div>
          <div>
            <label className="ui-label">Arrival Time</label>
            <input
              type="datetime-local"
              value={formData.arrival_time}
              onChange={(e) => setFormData({ ...formData, arrival_time: e.target.value })}
              className="ui-input"
              required
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
          <div>
            <label className="ui-label">Carrier (Optional)</label>
            <input
              type="text"
              value={formData.carrier}
              onChange={(e) => setFormData({ ...formData, carrier: e.target.value })}
              className="ui-input"
              placeholder="C1"
            />
          </div>
          <div>
            <label className="ui-label">Number (Optional)</label>
            <input
              type="text"
              value={formData.transport_number}
              onChange={(e) => setFormData({ ...formData, transport_number: e.target.value })}
              className="ui-input"
              placeholder="e.g. DL123"
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

export default TransportManager;
