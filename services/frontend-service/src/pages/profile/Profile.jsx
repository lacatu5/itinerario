import { useEffect, useState } from 'react';
import { getCurrentUser } from '../../services/authStore';
import { getUser, uploadProfileImage, deleteProfileImage, updateUser } from '../../services/users';
import { getUserItineraries } from '../../services/itineraries';
import { getItineraryLocations } from '../../services/locations';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGlobe, faMapMarkerAlt, faPlus, faUser, faCamera, faTrash, faEdit, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import '../../styles/itinerary-ui.css';
import '../../styles/ui.css';
import { resolveImageUrl } from '../../utils/url';
import { PageHeader, StatusBanner, EmptyState } from '../../components/ui';

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [upcomingTrips, setUpcomingTrips] = useState([]);
  const [tripsLoading, setTripsLoading] = useState(true);
  const [editingUsername, setEditingUsername] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [updatingUsername, setUpdatingUsername] = useState(false);
  const [tripImages, setTripImages] = useState({});

  const currentUser = getCurrentUser();

  useEffect(() => {
    if (!currentUser) {
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const userData = await getUser(currentUser.firebase_uid);
        setUser(userData);

        const itinerariesData = await getUserItineraries(currentUser.firebase_uid);
        const itineraries = itinerariesData?.items || itinerariesData || [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        let upcoming = itineraries
          .filter(trip => new Date(trip.start_date) >= today)
          .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
          .slice(0, 5);

        if (upcoming.length === 0 && itineraries && itineraries.length > 0) {
          upcoming = itineraries
            .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
            .slice(0, 5);
        }

        setUpcomingTrips(upcoming);

        const imagePromises = upcoming.map(async (trip) => {
          try {
            const locations = await getItineraryLocations(trip.id);
            if (locations && locations.length > 0 && locations[0].image_url) {
              return { tripId: trip.id, imageUrl: locations[0].image_url };
            }
          } catch (e) {
            console.error(`Failed to fetch locations for trip ${trip.id}:`, e);
          }
          return { tripId: trip.id, imageUrl: null };
        });

        const images = await Promise.all(imagePromises);
        const imageMap = {};
        images.forEach(({ tripId, imageUrl }) => {
          imageMap[tripId] = imageUrl;
        });
        setTripImages(imageMap);

      } catch (e) {
        setError('Failed to load profile');
      } finally {
        setLoading(false);
        setTripsLoading(false);
      }
    })();
  }, [currentUser]);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be smaller than 5MB');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const response = await uploadProfileImage(currentUser.firebase_uid, file);
      setUser(response.model || response);
    } catch (e) {
      setError(e.message || 'Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleImageDelete = async () => {
    if (!confirm('Are you sure you want to delete your profile image?')) {
      return;
    }

    setUploading(true);
    setError('');

    try {
      await deleteProfileImage(currentUser.firebase_uid);
      setUser({ ...user, profile_image_url: null });
    } catch (e) {
      setError(e.message || 'Failed to delete image');
    } finally {
      setUploading(false);
    }
  };

  const handleUsernameEdit = () => {
    setNewUsername(user?.username || '');
    setEditingUsername(true);
    setError('');
    setSuccess('');
  };

  const handleUsernameSave = async () => {
    if (!newUsername.trim()) {
      setError('Username cannot be empty');
      return;
    }

    const usernameRegex = /^[a-zA-Z0-9._]+$/;
    if (!usernameRegex.test(newUsername)) {
      setError('Username can only contain letters, numbers, dots and underscores');
      return;
    }

    if (newUsername.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    if (newUsername.length > 30) {
      setError('Username must be less than 30 characters');
      return;
    }

    setUpdatingUsername(true);
    setError('');

    try {
      const updatedUser = await updateUser(currentUser.firebase_uid, { username: newUsername });
      setUser(updatedUser);
      setEditingUsername(false);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Failed to update username');
    } finally {
      setUpdatingUsername(false);
    }
  };

  const handleUsernameCancel = () => {
    setEditingUsername(false);
    setNewUsername('');
    setError('');
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  if (!currentUser) {
    return (
      <div className="ui-page">
        <div className="ui-container">
          <div className="ui-card">
            <EmptyState
              variant="card"
              title="Please sign in"
              description="You need to be signed in to view your profile."
              icon= {
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <circle cx="32" cy="24" r="12" stroke="currentColor" strokeWidth="2"/>
                  <path d="M16 52c0-8.837 7.163-16 16-16s16 7.163 16 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              }
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card">
          {loading ? (
            <p className="ui-help">Loading profile...</p>
          ) : (
            <>
              <PageHeader
                title="Profile"
                subtitle="Manage your profile"
              />

              {error && (
                <StatusBanner
                  type="error"
                  message={error}
                  onDismiss={() => setError('')}
                />
              )}

              {success && (
                <StatusBanner
                  type="success"
                  message={success}
                  onDismiss={() => setSuccess('')}
                />
              )}

               {}
               <div className="panel section" style={ {
                 display: 'flex',
                 alignItems: 'flex-start',
                 gap: 32
               }}>
                 {}
                 <div style={ {
                   flexShrink: 0,
                   display: 'flex',
                   flexDirection: 'column',
                   alignItems: 'center'
                 }}>
                   <div style={ {
                     width: 120,
                     height: 120,
                     borderRadius: '50%',
                     overflow: 'hidden',
                     flexShrink: 0,
                     boxShadow: '0 0 0 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0,0,0,0.1)',
                     display: 'flex',
                     alignItems: 'center',
                     justifyContent: 'center'
                   }}>
                     {user?.profile_image_url ? (
                       <img
                         src={resolveImageUrl(user.profile_image_url)}
                         alt="Profile"
                         style={ {
                           width: '100%',
                           height: '100%',
                           objectFit: 'cover',
                           borderRadius: '50%'
                         }}
                       />
                     ) : (
                       <div style={ {
                         width: '100%',
                         height: '100%',
                         borderRadius: '50%',
                         background: 'linear-gradient(135deg, #e8e8e8 0%, #d4d4d4 100%)',
                         display: 'flex',
                         alignItems: 'center',
                         justifyContent: 'center',
                         color: '#666',
                         fontSize: 42,
                         fontWeight: 700,
                         textTransform: 'uppercase'
                       }}>
                         {user?.username?.charAt(0) || user?.name?.charAt(0) || user?.email?.charAt(0) || '?'}
                       </div>
                     )}
                   </div>

                   <div style={{ marginTop: 12 }}>
                     <input
                       type="file"
                       accept="image/*"
                       onChange={handleImageUpload}
                       disabled={uploading}
                       style={{ display: 'none' }}
                       id="profile-image-input"
                     />
                     <div style={ {
                       display: 'flex',
                       gap: 12,
                       justifyContent: 'center',
                       alignItems: 'center',
                       marginTop: 8
                     }}>
                       <label
                         htmlFor="profile-image-input"
                         style={ {
                           display: 'inline-flex',
                           alignItems: 'center',
                           justifyContent: 'center',
                           cursor: uploading ? 'not-allowed' : 'pointer',
                           opacity: uploading ? 0.6 : 1,
                           width: '40px',
                           height: '40px',
                           borderRadius: 'var(--radius-md)',
                           backgroundColor: '#FFFFFF',
                           border: '1px solid #E5E5E5',
                           color: 'var(--color-medium-gray)',
                           fontSize: '16px',
                           transition: 'all 0.2s ease',
                         boxShadow: '0 2px 4px rgba(0,0,0,0.04)'
                         }}
                         title={uploading ? 'Uploading...' : user?.profile_image_url ? 'Change Image' : 'Upload Image'}
                       >
                         <FontAwesomeIcon icon={user?.profile_image_url ? faEdit : faCamera} />
                       </label>

                       {user?.profile_image_url && (
                         <button
                           onClick={handleImageDelete}
                           disabled={uploading}
                           style={ {
                             display: 'inline-flex',
                             alignItems: 'center',
                             justifyContent: 'center',
                             cursor: uploading ? 'not-allowed' : 'pointer',
                             opacity: uploading ? 0.6 : 1,
                             width: '40px',
                             height: '40px',
                             borderRadius: 'var(--radius-md)',
                             backgroundColor: '#FFFFFF',
                             border: '1px solid #E5E5E5',
                             color: 'var(--color-medium-gray)',
                             fontSize: '16px',
                             transition: 'all 0.2s ease',
                           boxShadow: '0 2px 4px rgba(0,0,0,0.04)'
                           }}
                           title={uploading ? 'Deleting...' : 'Delete Image'}
                         >
                           <FontAwesomeIcon icon={faTrash} />
                         </button>
                       )}
                     </div>
                   </div>
                 </div>

                 {}
                 <div style={{ flex: 1, minWidth: 0 }}>
                   <h2 style={ {
                     fontSize: '2rem',
                     fontWeight: 700,
                     color: 'var(--color-black)',
                     marginBottom: 8,
                     lineHeight: 1.2
                   }}>
                     {user?.name || 'User'}
                   </h2>

                   {}
                   <div style={{ marginBottom: 16 }}>
                     {!editingUsername ? (
                       <div style={ {
                         display: 'flex',
                         alignItems: 'center',
                         gap: 12
                       }}>
                         <p style={ {
                           color: 'var(--color-medium-gray)',
                           fontSize: '1.1rem',
                           margin: 0,
                           fontWeight: 500
                         }}>
                           @{user?.username || 'no-username'}
                         </p>
                         <button
                           onClick={handleUsernameEdit}
                           disabled={uploading || updatingUsername}
                           style={ {
                             padding: '6px 12px',
                             backgroundColor: '#FFFFFF',
                             border: '1px solid #E5E5E5',
                             borderRadius: 'var(--radius-md)',
                             cursor: uploading || updatingUsername ? 'not-allowed' : 'pointer',
                             opacity: uploading || updatingUsername ? 0.6 : 1,
                             display: 'flex',
                             alignItems: 'center',
                             gap: 6,
                             fontSize: '0.85rem',
                             fontWeight: 500,
                             color: 'var(--color-medium-gray)',
                             transition: 'all 0.2s ease'
                           }}
                         >
                           <FontAwesomeIcon icon={faEdit} />
                           Edit
                         </button>
                       </div>
                     ) : (
                       <div style={ {
                         display: 'flex',
                         alignItems: 'center',
                         gap: 8
                       }}>
                         <div style={{ position: 'relative', flex: 1, maxWidth: 300 }}>
                           <span style={ {
                             position: 'absolute',
                             left: 12,
                             top: '50%',
                             transform: 'translateY(-50%)',
                             color: 'var(--color-medium-gray)',
                             fontSize: '1rem',
                             fontWeight: 500
                           }}>
                             @
                           </span>
                           <input
                             type="text"
                             value={newUsername}
                             onChange={(e) => setNewUsername(e.target.value)}
                             placeholder="username"
                             style={ {
                               width: '100%',
                               padding: '10px 12px 10px 28px',
                               border: '1px solid #E5E5E5',
                               borderRadius: 'var(--radius-md)',
                               fontSize: '1rem',
                               fontFamily: 'inherit'
                             }}
                             disabled={updatingUsername}
                             autoFocus
                           />
                         </div>
                         <button
                           onClick={handleUsernameSave}
                           disabled={updatingUsername}
                           style={ {
                             padding: '10px 16px',
                             backgroundColor: 'var(--color-black)',
                             color: 'white',
                             border: 'none',
                             borderRadius: 'var(--radius-md)',
                             cursor: updatingUsername ? 'not-allowed' : 'pointer',
                             opacity: updatingUsername ? 0.6 : 1,
                             display: 'flex',
                             alignItems: 'center',
                             gap: 6,
                             fontSize: '0.9rem',
                             fontWeight: 600,
                             transition: 'all 0.2s ease'
                           }}
                         >
                           <FontAwesomeIcon icon={faCheck} />
                           {updatingUsername ? 'Saving...' : 'Save'}
                         </button>
                         <button
                           onClick={handleUsernameCancel}
                           disabled={updatingUsername}
                           style={ {
                             padding: '10px 16px',
                             backgroundColor: '#FFFFFF',
                             color: 'var(--color-medium-gray)',
                             border: '1px solid #E5E5E5',
                             borderRadius: 'var(--radius-md)',
                             cursor: updatingUsername ? 'not-allowed' : 'pointer',
                             opacity: updatingUsername ? 0.6 : 1,
                             display: 'flex',
                             alignItems: 'center',
                             gap: 6,
                             fontSize: '0.9rem',
                             fontWeight: 600,
                             transition: 'all 0.2s ease'
                           }}
                         >
                           <FontAwesomeIcon icon={faTimes} />
                           Cancel
                         </button>
                       </div>
                     )}
                   </div>

                   <p style={ {
                     color: 'var(--color-light-gray)',
                     fontSize: '0.95rem',
                     marginBottom: 16,
                     fontWeight: 400
                   }}>
                     {user?.email}
                   </p>

                   {}
                   <div style={ {
                     display: 'grid',
                     gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                     gap: 24,
                     marginTop: 16
                   }}>
                     <div>
                       <div style={ {
                         fontSize: '1.75rem',
                         fontWeight: 700,
                         color: 'var(--color-black)',
                         marginBottom: 4
                       }}>
                         {upcomingTrips.filter(trip => new Date(trip.start_date) >= new Date()).length}
                       </div>
                       <div style={ {
                         color: 'var(--color-light-gray)',
                         fontSize: '1rem',
                         fontWeight: 500
                       }}>
                         Upcoming Trips
                       </div>
                     </div>
                     <div>
                       <div style={ {
                         fontSize: '1.75rem',
                         fontWeight: 700,
                         color: 'var(--color-black)',
                         marginBottom: 4
                       }}>
                         {user?.created_at ? new Date(user.created_at).getFullYear() : 'N/A'}
                       </div>
                       <div style={ {
                         color: 'var(--color-light-gray)',
                         fontSize: '1rem',
                         fontWeight: 500
                       }}>
                         Member Since
                       </div>
                     </div>
                   </div>
                 </div>
               </div>

              {}
              <div className="panel section">
                <div style={ {
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 20
                }}>
                  <h2 className="ui-subtitle" style={ {
                    marginBottom: 0,
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    color: 'var(--color-black)'
                  }}>
                    {upcomingTrips.length > 0 && new Date(upcomingTrips[0].start_date) >= new Date() ? 'Next Trips' : 'Recent Trips'}
                  </h2>
                  <Link
                    to="/itineraries"
                    className="ui-button ui-button-secondary"
                    style={ {
                      fontSize: 13,
                      padding: '8px 16px',
                      fontWeight: 500
                    }}
                  >
                    View All
                  </Link>
                </div>

                {tripsLoading ? (
                  <div style={ {
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    padding: 40,
                    backgroundColor: '#FFFFFF',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid #F0F0F0'
                  }}>
                    <p className="ui-help" style={{ margin: 0, fontSize: '0.95rem' }}>Loading trips...</p>
                  </div>
                ) : upcomingTrips.length === 0 ? (
                  <div style={ {
                    padding: 40,
                    backgroundColor: '#FFFFFF',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid #F0F0F0',
                    textAlign: 'center',
                    position: 'relative'
                  }}>
                    <div style={ {
                      fontSize: '3rem',
                      marginBottom: 20,
                      color: 'var(--color-light-gray)',
                      fontWeight: 'normal'
                    }}>
                      <FontAwesomeIcon icon={faGlobe} />
                    </div>
                    <h3 style={ {
                      fontWeight: 700,
                      fontSize: '1.5rem',
                      marginBottom: 12,
                      margin: 0,
                      color: 'var(--color-black)'
                    }}>
                      Time to plan your next adventure!
                    </h3>
                    <p style={ {
                      marginBottom: 32,
                      fontSize: '1.1rem',
                      color: 'var(--color-light-gray)',
                      lineHeight: 1.5
                    }}>
                      Create your first itinerary and start exploring the world
                    </p>
                    <Link
                      className="ui-button"
                      to="/itineraries/new"
                      style={ {
                        backgroundColor: 'var(--color-black)',
                        color: 'var(--color-white)',
                        fontWeight: 600,
                        padding: '14px 28px',
                        borderRadius: 'var(--radius-md)',
                        textDecoration: 'none',
                        display: 'inline-block',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      Create New Trip
                    </Link>
                  </div>
                ) : (
                   <div style={ {
                     display: 'grid',
                     gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                     gap: 24
                   }}>
                     {}
                     {upcomingTrips.slice(0, 4).map((trip) => (
                       <Link
                         key={trip.id}
                         to={`/itineraries/${trip.id}`}
                         style={ {
                           display: 'block',
                           padding: 0,
                           backgroundColor: '#FFFFFF',
                           borderRadius: 'var(--radius-lg)',
                           border: '1px solid #F0F0F0',
                           textDecoration: 'none',
                           transition: 'all 0.3s ease',
                           boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                         overflow: 'hidden'
                         }}
                       >
                         {}
                         {tripImages[trip.id] ? (
                           <div style={ {
                             height: 140,
                             backgroundImage: `url(${resolveImageUrl(tripImages[trip.id])})`,
                             backgroundSize: 'cover',
                             backgroundPosition: 'center',
                             position: 'relative'
                           }}>
                             <div style={ {
                               position: 'absolute',
                               bottom: 0,
                               left: 0,
                               right: 0,
                               height: '50%',
                               background: 'linear-gradient(to top, rgba(0,0,0,0.3), transparent)'
                             }} />
                           </div>
                         ) : (
                           <div style={ {
                             height: 140,
                             backgroundColor: '#E5E7EB',
                             display: 'flex',
                             alignItems: 'center',
                             justifyContent: 'center',
                             fontSize: '2.5rem',
                             color: '#6B7280'
                           }}>
                             <FontAwesomeIcon icon={faCamera} />
                           </div>
                         )}

                         <div style={{ padding: 20 }}>
                           <div style={ {
                             display: 'flex',
                             justifyContent: 'space-between',
                             alignItems: 'flex-start',
                             marginBottom: 8
                           }}>
                             <h3 style={ {
                               fontWeight: 700,
                               color: 'var(--color-black)',
                               fontSize: '1.1rem',
                               margin: 0,
                               lineHeight: 1.3,
                               flex: 1
                             }}>
                               {trip.title}
                             </h3>
                             <span style={ {
                               fontSize: '0.8rem',
                               color: 'var(--color-white)',
                               fontWeight: 600,
                               backgroundColor: 'var(--color-medium-gray)',
                               padding: '4px 8px',
                               borderRadius: '12px',
                               whiteSpace: 'nowrap',
                               marginLeft: 12
                             }}>
                               {new Date(trip.start_date).toLocaleDateString('es-ES', {
                                 month: 'short',
                                 day: 'numeric'
                               })}
                             </span>
                           </div>

                           <div style={ {
                             color: 'var(--color-medium-gray)',
                             fontSize: '0.9rem',
                             fontWeight: 500,
                             marginBottom: 6
                           }}>
                             <FontAwesomeIcon icon={faMapMarkerAlt} style={{ marginRight: 6 }} />
                             {trip.destination}
                           </div>

                           {trip.short_description && (
                             <p style={ {
                               color: 'var(--color-light-gray)',
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
                         </div>
                       </Link>
                     ))}

                     {}
                     {upcomingTrips.length < 4 && (
                       <Link
                         to="/itineraries/new"
                         style={ {
                           display: 'flex',
                           flexDirection: 'column',
                           alignItems: 'center',
                           justifyContent: 'center',
                           padding: 28,
                           backgroundColor: '#FAFBFC',
                           border: '2px dashed #E0E0E0',
                           borderRadius: 'var(--radius-lg)',
                           textDecoration: 'none',
                           transition: 'all 0.3s ease',
                           minHeight: 220,
                         color: 'var(--color-medium-gray)'
                         }}
                       >
                         <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>
                           <FontAwesomeIcon icon={faPlus} />
                         </div>
                         <h3 style={ {
                           fontSize: '1rem',
                           fontWeight: 600,
                           marginBottom: 6,
                           textAlign: 'center'
                         }}>
                           Plan New Trip
                         </h3>
                         <p style={ {
                           fontSize: '0.85rem',
                           textAlign: 'center',
                           margin: 0,
                           opacity: 0.8
                         }}>
                           Create your next adventure
                         </p>
                       </Link>
                     )}
                   </div>
                )}
              </div>


            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;
