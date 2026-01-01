import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/itinerary-ui.css';
import { signOutUser } from '../../services/firebase';

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleSignOut = async () => {
      try {
        await signOutUser();
        setTimeout(() => {
          navigate('/');
        }, 1000);
      } catch (error) {
        console.error('Error signing out:', error);
        navigate('/');
      }
    };

    handleSignOut();
  }, [navigate]);

  return (
    <div className="ui-page">
      <div className="ui-container">
        <div className="ui-card ui-center">
          <h1 className="ui-title">Signing you out…</h1>
          <p className="ui-subtitle">Redirecting to home shortly.</p>
        </div>
      </div>
    </div>
  );
}

export default Logout;
