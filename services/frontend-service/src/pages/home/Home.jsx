import '../../styles/Home.css';
import carVideoWebm from '../../assets/video_car.webm';
import { useEffect, useRef, useState } from 'react';
import { getCurrentUser, onUserChange } from '../../services/authStore';
import { Link } from 'react-router-dom';

function Home() {
  const [user, setUser] = useState(getCurrentUser());
  useEffect(() => {
    const unsubscribe = onUserChange((u) => setUser(u));
    return () => unsubscribe();
  }, []);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const [shouldLoadVideo, setShouldLoadVideo] = useState(false);
  const [preloadMode, setPreloadMode] = useState('none');
  const heroRef = useRef(null);

  const [videoLoaded, setVideoLoaded] = useState(false);
  const [videoError, setVideoError] = useState(false);

  useEffect(() => {
    let slowNetwork = false;
    try {
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      slowNetwork = !!conn && (conn.saveData || ['slow-2g', '2g'].includes(conn.effectiveType));
    } catch (e) {
      slowNetwork = false;
    }

    const should = !prefersReducedMotion && !slowNetwork;
    setPreloadMode(should ? 'metadata' : 'none');

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShouldLoadVideo(should);
          observer.disconnect();
        }
      },
      { root: null, rootMargin: '200px', threshold: 0.01 }
    );

    if (heroRef.current) {
      observer.observe(heroRef.current);
    } else {
      setShouldLoadVideo(should);
    }

    return () => observer.disconnect();
  }, [prefersReducedMotion]);

  const features = [
 {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
      ),
      title: 'Plan Destinations',
      description: 'Organize your dream locations'
    },
 {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
      ),
      title: 'Schedule Activities',
      description: 'Create day-by-day itineraries'
    },
 {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      title: 'Share & Connect',
      description: 'Connect with fellow travelers'
    }
  ];

  return (
    <div className="page-layout home" ref={heroRef}>
      <video
        className={`hero-video ${videoLoaded && !videoError ? 'is-visible' : ''}`}
        autoPlay={!prefersReducedMotion}
        loop={!prefersReducedMotion}
        muted
        playsInline
        preload={preloadMode}
        onLoadedData={() => setVideoLoaded(true)}
        onError={() => setVideoError(true)}
      >
        {shouldLoadVideo && <source src={carVideoWebm} type="video/webm" />}
      </video>

      <div
        className={`hero-placeholder ${videoError ? 'is-error' : ''} ${videoLoaded ? 'is-hidden' : ''}`}
        role="status"
        aria-live="polite"
      >
        <span className="visually-hidden">
          {videoError ? 'Video could not be loaded' : 'Loading…'}
        </span>
      </div>

      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-main">
            <h1 className="hero-title">itinerario</h1>
            <p className="hero-subtitle">
              {user
                ? `Welcome back! Ready to plan your next adventure?`
                : `Plan, organize, and explore your journeys beautifully.`
              }
            </p>

            <div className="hero-cta">
              {user ? (
                <>
                  <Link to="/itineraries/new" className="hero-btn hero-btn--primary">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Create New Trip
                  </Link>
                  <Link to="/itineraries" className="hero-btn hero-btn--secondary">
                    View My Trips
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/register" className="hero-btn hero-btn--primary">
                    Get Started Free
                  </Link>
                  <Link to="/login" className="hero-btn hero-btn--secondary">
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>

        {}
        <div className="hero-features-bar">
          {features.map((feature, index) => (
            <div key={index} className="hero-feature-card">
              <div className="hero-feature-icon">{feature.icon}</div>
              <div className="hero-feature-content">
                <h3 className="hero-feature-title">{feature.title}</h3>
                <p className="hero-feature-desc">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {}
      <div className="contact-widget">
        <div className="contact-card contact-card--floating">
          <div className="contact-card-content">
            <div className="contact-header">
              <span className="contact-label">Created by</span>
              <h3>Tudor C. Lacatus Cosma</h3>
            </div>
            <a href="https://github.com/lacatu5" target="_blank" rel="noopener noreferrer" className="contact-link">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
