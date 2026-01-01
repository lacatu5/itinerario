import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import './Navbar.css';

function Navbar({ items = [{ to: '/', label: 'Home' }] }) {
  const location = useLocation();
  const [compact, setCompact] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const dropdownRef = useRef(null);
  const [imageKey, setImageKey] = useState(0);

  const isActive = (to) => {
    const path = location.pathname;
    if (to === '/itineraries') {
      return path.startsWith('/itineraries') && path !== '/itineraries/new';
    }
    return path === to;
  };

  const isDropdownActive = (dropdown) => {
    return dropdown?.some(item => isActive(item.to));
  };

  useEffect(() => {
    const scroller = document.querySelector('.main-content');
    let last = scroller ? scroller.scrollTop : window.scrollY;
    const onScroll = () => {
      const y = scroller ? scroller.scrollTop : window.scrollY;
      const goingDown = y > last;
      if (goingDown && y > 14) {
        setCompact(true);
      } else if (!goingDown && y < 10) {
        setCompact(false);
      }
      last = y;
    };
    (scroller || window).addEventListener('scroll', onScroll, { passive: true });
    return () => (scroller || window).removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setOpenDropdown(null);
  }, [location.pathname]);

  useEffect(() => {
    const profileItem = items.find(item => item.isProfile);
    if (profileItem?.photoURL) {
      setImageKey(prev => prev + 1);
    }
  }, [items]);

  const handleDropdownToggle = (label) => {
    setOpenDropdown(openDropdown === label ? null : label);
  };

  const renderProfileAvatar = (item) => {
    if (item.photoURL) {
      return (
        <img
          key={imageKey}
          src={item.photoURL}
          alt="Profile"
          className="nav-avatar-img"
          onLoad={(e) => {
            e.target.removeAttribute('data-retry-count');
            e.target.style.display = 'block';
            e.target.nextSibling.style.display = 'none';
          }}
          onError={(e) => {
            if (!e.target.hasAttribute('data-retry-count')) {
              e.target.setAttribute('data-retry-count', '1');
              const url = new URL(e.target.src);
              url.searchParams.set('t', Date.now());
              e.target.src = url.toString();
            } else {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }
          }}
        />
      );
    }
    return null;
  };

  const renderProfileInitial = (item) => (
    <span
      className="nav-avatar-initial"
      style={{ display: item.photoURL ? 'none' : 'flex' }}
    >
      {item.initial}
    </span>
  );


  return (
    <nav className={`navbar${compact ? ' navbar--compact' : ''}`}>
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <img src="/logo.svg" alt="itinerario logo" className="nav-logo-img" />
        </Link>
        <div className="nav-menu" ref={dropdownRef}>
          {items.map((item, index) => (
            item.dropdown ? (
              <div key={item.label || `profile-${index}`} className="nav-dropdown-wrapper">
                <button
                  className={`nav-link nav-dropdown-trigger${isDropdownActive(item.dropdown) ? ' active' : ''}${item.isProfile ? ' nav-profile-btn' : ''}`}
                  onClick={() => handleDropdownToggle(item.label || `profile-${index}`)}
                  aria-expanded={openDropdown === (item.label || `profile-${index}`)}
                  aria-haspopup="true"
                >
                  {item.isProfile ? (
                    <span className="nav-avatar">
                      {renderProfileAvatar(item)}
                      {renderProfileInitial(item)}
                    </span>
                  ) : (
                    <>
                      {item.label}
                      <svg className="dropdown-arrow" width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </>
                  )}
                </button>
                {openDropdown === (item.label || `profile-${index}`) && (
                  <div className={`nav-dropdown${item.isProfile ? ' nav-dropdown--right' : ''}`}>
                    {item.isProfile && item.username && (
                      <div className="nav-dropdown-header">
                        <span className="nav-dropdown-label">Signed in as</span>
                        <span className="nav-dropdown-username">@{item.username}</span>
                      </div>
                    )}
                    {item.dropdown.map((subItem) => (
                      <Link
                        key={subItem.to}
                        to={subItem.to}
                        className={`nav-dropdown-item${isActive(subItem.to) ? ' active' : ''}${subItem.isDanger ? ' nav-dropdown-item--danger' : ''}`}
                      >
                        {subItem.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <Link
                key={item.to}
                to={item.to}
                className={`nav-link${isActive(item.to) ? ' active' : ''}`}
                aria-current={isActive(item.to) ? 'page' : undefined}
              >
                {item.label}
              </Link>
            )
          ))}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
