import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/home/Home';
import Register from './pages/auth/Register';
import Login from './pages/auth/Login';
import CreateItinerary from './pages/itineraries/CreateItinerary';
import Itineraries from './pages/itineraries/Itineraries';
import ItineraryDetail from './pages/itineraries/ItineraryDetail';
import EditItinerary from './pages/itineraries/EditItinerary';
import Profile from './pages/profile/Profile';
import Social from './pages/social/Social';
import Destinations from './pages/destinations/Destinations';
import CreateDestination from './pages/destinations/CreateDestination';
import DestinationDetail from './pages/destinations/DestinationDetail';
import EditDestination from './pages/destinations/EditDestination';
import TravelAlerts from './pages/travel-alerts/TravelAlerts';
import './App.css';
import { useEffect, useState } from 'react';
import { getCurrentUser, getUserProfile, onUserChange } from './services/authStore';
import { getUser } from './services/users';
import Logout from './pages/auth/Logout';
import SearchTrips from './pages/search/SearchTrips';
import { resolveImageUrl } from './utils/url';

function AppShell({ navItems }) {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <div className={`App ${isHomePage ? 'app--home' : 'app--internal'}`}>
      <Navbar items={navItems} />
      <main className={`main-content ${isHomePage ? 'main-content--home' : 'main-content--internal'}`}>
        <div className="route-wrapper fade-slide-in">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/search" element={<SearchTrips />} />
            <Route path="/itineraries" element={<Itineraries />} />
            <Route path="/itineraries/new" element={<CreateItinerary />} />
            <Route path="/itineraries/:id" element={<ItineraryDetail />} />
            <Route path="/itineraries/:id/edit" element={<EditItinerary />} />
            <Route path="/destinations" element={<Destinations />} />
            <Route path="/destinations/new" element={<CreateDestination />} />
            <Route path="/destinations/:id" element={<DestinationDetail />} />
            <Route path="/destinations/:id/edit" element={<EditDestination />} />
            <Route path="/travel-alerts" element={<TravelAlerts />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/social" element={<Social />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="*" element={<Home />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(getCurrentUser());
  const [userProfile, setUserProfile] = useState(getUserProfile());

  useEffect(() => {
    const unsubscribe = onUserChange((u) => {
      setUser(u);
      if (u) {
        const cachedProfile = getUserProfile();
        if (cachedProfile) {
          setUserProfile(cachedProfile);
        } else {
          getUser(u.id).then(profile => {
            setUserProfile(profile);
          }).catch(() => {});
        }
      } else {
        setUserProfile(null);
      }
    });
    return () => unsubscribe();
  }, []);

  const getUserInitial = () => {
    if (userProfile?.username) return userProfile.username.charAt(0).toUpperCase();
    if (userProfile?.name) return userProfile.name.charAt(0).toUpperCase();
    if (user?.displayName) return user.displayName.charAt(0).toUpperCase();
    if (user?.name) return user.name.charAt(0).toUpperCase();
    if (user?.email) return user.email.charAt(0).toUpperCase();
    return '?';
  };

  const getProfileImageUrl = () => {
    if (userProfile?.profile_image_url) {
      return resolveImageUrl(userProfile.profile_image_url);
    }
    if (user?.photoURL) {
      return user.photoURL;
    }
    return null;
  };

  const navItems = [
    { to: '/', label: 'Home' },
    { to: '/search', label: 'Explore' },
    ...(user ? [
 {
        label: 'My Trips',
        dropdown: [
          { to: '/itineraries', label: 'My Itineraries' },
          { to: '/itineraries/new', label: 'Create New' },
          { to: '/destinations', label: 'Saved Destinations' },
        ]
      },
      { to: '/social', label: 'Community' },
    ] : []),
    ...(user ? [
 {
        isProfile: true,
        photoURL: getProfileImageUrl(),
        initial: getUserInitial(),
        username: userProfile?.username || user?.name || user?.email?.split('@')[0],
        dropdown: [
          { to: '/profile', label: 'Profile' },
          { to: '/travel-alerts', label: 'Travel Alerts' },
          { to: '/logout', label: 'Sign Out', isDanger: true },
        ]
      }
    ] : [
      { to: '/login', label: 'Sign In' },
    ]),
  ];
  return (
    <Router>
      <AppShell navItems={navItems} />
    </Router>
  );
}

export default App;
