import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faEnvelope, faLock, faUserPlus } from '@fortawesome/free-solid-svg-icons';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';
import '../../styles/itinerary-ui.css';
import { createUserWithEmail, signInWithGoogle } from '../../services/firebase';

function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();


  async function handleEmailRegister(e) {
    e.preventDefault();

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await createUserWithEmail(email, password, name);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleRegister() {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ui-page" style={{ display: 'flex', alignItems: 'center' }}>
      <div className="ui-container" style={{ maxWidth: 420, margin: '0 auto', width: '100%' }}>
        <div className="ui-card" style={{ padding: '32px 32px 16px' }}>
          {}
          <div style={ {
            textAlign: 'center',
            marginBottom: 24
          }}>
            <div style={ {
              width: 48,
              height: 48,
              backgroundColor: '#F8F9FA',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px',
              border: '1px solid #E5E5E5'
            }}>
              <FontAwesomeIcon
                icon={faUserPlus}
                style={ {
                  fontSize: '1.2rem',
                  color: 'var(--color-medium-gray)'
                }}
              />
            </div>
            <h1 style={ {
              fontSize: '1.75rem',
              fontWeight: 700,
              color: 'var(--color-black)',
              marginBottom: 6
            }}>
              Create Account
            </h1>
            <p style={ {
              color: 'var(--color-light-gray)',
              fontSize: '0.9rem',
              margin: 0
            }}>
              Join us to start planning your trips
            </p>
          </div>

          {}
          <div style={{ marginBottom: 24 }}>
            <button
              type="button"
              onClick={handleGoogleRegister}
              disabled={loading}
              style={ {
                width: '100%',
                padding: '12px 20px',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E5E5E5',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.95rem',
                fontWeight: 600,
                color: 'var(--color-black)',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 12
              }}
            >
              <FontAwesomeIcon
                icon={faGoogle}
                style={ {
                  fontSize: '1rem',
                  color: 'var(--color-medium-gray)'
                }}
              />
              Continue with Google
            </button>
          </div>

          {}
          <div style={ {
            display: 'flex',
            alignItems: 'center',
            marginBottom: 24
          }}>
            <div style={ {
              flex: 1,
              height: '1px',
              backgroundColor: '#E5E5E5'
            }}></div>
            <span style={ {
              padding: '0 16px',
              fontSize: '0.85rem',
              color: 'var(--color-light-gray)',
              fontWeight: 500
            }}>
              or
            </span>
            <div style={ {
              flex: 1,
              height: '1px',
              backgroundColor: '#E5E5E5'
            }}></div>
          </div>

          {}
          {error && (
            <div style={ {
              marginBottom: 20,
              padding: 12,
              backgroundColor: '#F9F9F9',
              border: '1px solid #E5E5E5',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-black)',
              fontSize: '0.85rem'
            }}>
              {error}
            </div>
          )}

          {}
          <form onSubmit={handleEmailRegister} style={{ marginBottom: 20 }}>
            <div style={{ marginBottom: 16 }}>
              <label style={ {
                display: 'block',
                marginBottom: 6,
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-black)'
              }}>
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={ {
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E5E5E5',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.9rem',
                  backgroundColor: '#FFFFFF',
                  transition: 'border-color 0.2s ease',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--color-primary)'}
                onBlur={(e) => e.target.style.borderColor = '#E5E5E5'}
                placeholder="Enter your full name"
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={ {
                display: 'block',
                marginBottom: 6,
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-black)'
              }}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={ {
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E5E5E5',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.9rem',
                  backgroundColor: '#FFFFFF',
                  transition: 'border-color 0.2s ease',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--color-primary)'}
                onBlur={(e) => e.target.style.borderColor = '#E5E5E5'}
                placeholder="Enter your email"
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={ {
                display: 'block',
                marginBottom: 6,
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-black)'
              }}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={ {
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E5E5E5',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.9rem',
                  backgroundColor: '#FFFFFF',
                  transition: 'border-color 0.2s ease',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--color-primary)'}
                onBlur={(e) => e.target.style.borderColor = '#E5E5E5'}
                placeholder="Create a password"
              />
              <div style={ {
                fontSize: '0.75rem',
                color: 'var(--color-light-gray)',
                marginTop: 4
              }}>
                Must be at least 6 characters long
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={ {
                width: '100%',
                padding: '12px 20px',
                backgroundColor: 'var(--color-primary)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                transition: 'all 0.2s ease'
              }}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          {}
          <div style={ {
            textAlign: 'center',
            paddingTop: 16,
            borderTop: '1px solid #F0F0F0'
          }}>
            <p style={ {
              color: 'var(--color-light-gray)',
              fontSize: '0.85rem',
              margin: 0
            }}>
              Already have an account?{' '}
              <Link
                to="/login"
                style={ {
                  color: 'var(--color-primary)',
                  textDecoration: 'none',
                  fontWeight: 600
                }}
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;
