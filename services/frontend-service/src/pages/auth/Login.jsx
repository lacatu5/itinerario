import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope, faLock, faSignInAlt } from '@fortawesome/free-solid-svg-icons';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';
import '../../styles/itinerary-ui.css';
import { signInWithEmail, signInWithGoogle } from '../../services/firebase';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();


  async function handleEmailLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await signInWithEmail(email.trim(), password);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleLogin() {
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
                icon={faSignInAlt}
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
              Welcome Back
            </h1>
            <p style={ {
              color: 'var(--color-light-gray)',
              fontSize: '0.9rem',
              margin: 0
            }}>
              Sign in to your account to continue
            </p>
          </div>

          {}
          <div style={{ marginBottom: 24 }}>
            <button
              type="button"
              onClick={handleGoogleLogin}
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
          <form onSubmit={handleEmailLogin} style={{ marginBottom: 20 }}>
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
                placeholder="Enter your password"
              />
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
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          {}
          <div style={ {
            textAlign: 'center',
            paddingTop: 16,
            borderTop: '1px solid #F0F0F0'
          }}>
            <p style={ {
              color: 'var(--color-medium-gray)',
              fontSize: '0.85rem',
              margin: 0
            }}>
              Don't have an account?{' '}
              <Link
                to="/register"
                style={ {
                  color: 'var(--color-black)',
                  textDecoration: 'none',
                  fontWeight: 600
                }}
              >
                Sign up here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
