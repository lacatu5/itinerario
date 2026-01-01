import { useEffect, useState } from 'react';
import '../../styles/itinerary-ui.css';
import { getItinerary, updateItinerary } from '../../services/itineraries';
import { getCurrentUser } from '../../services/authStore';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faCalendarAlt, faSave, faArrowLeft, faMap } from '@fortawesome/free-solid-svg-icons';
import { Link, useNavigate, useParams } from 'react-router-dom';
import MapPicker from '../../components/MapPicker';

function toDateInputValue(d) {
  if (!d) return '';
  try {
    const date = new Date(d);
    const tzOffset = date.getTimezoneOffset() * 60000;
    return new Date(date.getTime() - tzOffset).toISOString().slice(0, 10);
  } catch {
    return String(d).slice(0, 10);
  }
}

export default function EditItinerary() {
  const { id } = useParams();
  const navigate = useNavigate();
  const user = getCurrentUser();

  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');
  const [showMap, setShowMap] = useState(false);
  const [form, setForm] = useState( {
    title: '',
    destination: '',
    start_date: '',
    end_date: '',
    short_description: '',
    detail_description: '',
    image_url: null,
    latitude: '',
    longitude: '',
    address: ''
  });

  useEffect(() => {
    (async () => {
      try {
        const item = await getItinerary(id);
        if (!user || user.id !== item.owner_id) {
          navigate(`/itineraries/${id}`);
          return;
        }
        setForm( {
          title: item.title || '',
          destination: item.destination || '',
          start_date: toDateInputValue(item.start_date),
          end_date: toDateInputValue(item.end_date),
          short_description: item.short_description || '',
          detail_description: item.detail_description || '',
          image_url: item.image_url || null,
          latitude: item.latitude || '',
          longitude: item.longitude || '',
          address: item.address || ''
        });
      } catch (e) {
        setError('No se pudo cargar el itinerario.');
      } finally {
        setFetching(false);
      }
    })();
  }, [id]);

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleMapChange = (locationData) => {
    if (locationData) {
      const destParts = [];
      if (locationData.city) destParts.push(locationData.city);
      if (locationData.region) destParts.push(locationData.region);
      if (locationData.country) destParts.push(locationData.country);

      const destination = destParts.length > 0
        ? destParts.join(', ')
        : locationData.name || '';

      setForm((f) => ( {
        ...f,
        destination: destination,
        latitude: String(locationData.lat),
        longitude: String(locationData.lng),
        address: locationData.address || ''
      }));
    } else {
      setForm((f) => ( {
        ...f,
        destination: '',
        latitude: '',
        longitude: '',
        address: ''
      }));
    }
  };

  const mapValue = form.latitude && form.longitude ? {
    lat: parseFloat(form.latitude),
    lng: parseFloat(form.longitude),
    address: form.address
  } : null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = {
        title: form.title,
        destination: form.destination,
        start_date: form.start_date,
        end_date: form.end_date || null,
        short_description: form.short_description,
        detail_description: form.detail_description,
        image_url: form.image_url || null,
        latitude: form.latitude || null,
        longitude: form.longitude || null,
        address: form.address || null
      };
      await updateItinerary(id, payload);
      navigate(`/itineraries/${id}`);
    } catch (e) {
      setError('No se pudo guardar los cambios.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          {}
          <div style={ {
            marginBottom: 32,
            padding: 32,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            <div style={ {
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              flexWrap: 'wrap',
              gap: 24
            }}>
              <div>
                <h1 style={ {
                  fontSize: '2.5rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 8,
                  lineHeight: 1.2
                }}>
                  Edit Itinerary
                </h1>
                <p style={ {
                  color: 'var(--color-medium-gray)',
                  fontSize: '1.1rem',
                  fontWeight: 500,
                  margin: 0
                }}>
                  Actualiza la información de tu viaje
                </p>
              </div>

              <Link
                to={`/itineraries/${id}`}
                className="ui-button ui-button-secondary"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <FontAwesomeIcon icon={faArrowLeft} />
                Volver al detalle
              </Link>
            </div>
          </div>

          {}
          <div style={ {
            padding: 32,
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid #F0F0F0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            {fetching ? (
              <div className="ui-center">Cargando…</div>
            ) : (
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
                      fontSize: '1.25rem',
                      fontWeight: 700,
                      color: 'var(--color-black)',
                      margin: 0,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12
                    }}>
                      <FontAwesomeIcon icon={faMap} style={{ color: 'var(--color-medium-gray)' }} />
                      Update Destination
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
                      placeholder="Search for your destination..."
                      height="250px"
                    />
                  )}
                </div>

                {}
                <div className="ui-row">
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Título del viaje *
                    </label>
                    <input className="ui-input" value={form.title} onChange={update('title')} />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Destino *
                    </label>
                    <input className="ui-input" value={form.destination} onChange={update('destination')} />
                  </div>
                </div>

                <div className="ui-row">
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Fecha de inicio *
                    </label>
                    <input className="ui-input" type="date" value={form.start_date} onChange={update('start_date')} />
                  </div>
                  <div>
                    <label className="ui-label">
                      <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: 6, color: 'var(--color-medium-gray)' }} />
                      Fecha de fin
                    </label>
                    <input className="ui-input" type="date" value={form.end_date} onChange={update('end_date')} min={form.start_date} />
                  </div>
                </div>

                <div>
                  <label className="ui-label">Descripción corta *</label>
                  <input className="ui-input" value={form.short_description} onChange={update('short_description')} maxLength={90} />
                </div>

                <div>
                  <label className="ui-label">Descripción detallada</label>
                  <textarea className="ui-textarea" value={form.detail_description} onChange={update('detail_description')} rows={6} />
                </div>

                {error && (
                  <div className="ui-help" style={{ color: 'var(--color-black)' }}>{error}</div>
                )}

                <div className="ui-actions">
                  <button className="ui-button ui-button-outline" type="button" onClick={() => navigate(`/itineraries/${id}`)}>
                    Cancelar
                  </button>
                  <button className="ui-button" type="submit" disabled={loading} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                    <FontAwesomeIcon icon={faSave} />
                    {loading ? 'Guardando…' : 'Guardar cambios'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
