import { useState, useEffect } from 'react';
import { getCurrentUser } from '../../services/authStore';
import { getUser, searchUsers } from '../../services/users';
import { getConversations, createConversation } from '../../services/chat';
import {
  followUser,
  getFollowers,
  getFollowing
} from '../../services/social';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '../../styles/ui.css';
import './Social.css';
import UserCard from './components/UserCard';
import ConversationsList from './components/ConversationsList';
import ChatWindow from './components/ChatWindow';
import Feed from './components/Feed';
import { PageHeader, StatusBanner, EmptyState } from '../../components/ui';
import {
  faUsers,
  faEnvelope,
  faSearch,
  faComments,
  faUserFriends,
  faGlobe,
  faUser,
  faStream
} from '@fortawesome/free-solid-svg-icons';

function Social() {
  const [activeTab, setActiveTab] = useState('feed');
  const [activePeopleTab, setActivePeopleTab] = useState('discover');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [followersDetails, setFollowersDetails] = useState([]);
  const [followingDetails, setFollowingDetails] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingFollowers, setLoadingFollowers] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [retryCount, setRetryCount] = useState(0);

  const currentUser = getCurrentUser();

  useEffect(() => {
    if (!currentUser) return;

    const loadSocialData = async () => {
      setLoading(true);
      setError('');
      try {
        const [followersData, followingData] = await Promise.all([
          getFollowers(currentUser.firebase_uid),
          getFollowing(currentUser.firebase_uid)
        ]);

        setFollowers(followersData || []);
        setFollowing(followingData || []);

        // Try to load conversations separately (requires auth)
        try {
          const conversationsData = await getConversations();
          setConversations(conversationsData || []);
        } catch (convErr) {
          // If 401, conversations require auth - just skip them
          if (convErr.status === 401) {
            console.warn('Conversations require authentication, skipping');
            setConversations([]);
          } else {
            throw convErr;
          }
        }
      } catch (err) {
        console.error('Error loading social data:', err);
        setError('Failed to load social data');
      } finally {
        setLoading(false);
      }
    };

    loadSocialData();
  }, [currentUser]);

  useEffect(() => {
    if (!currentUser || activeTab !== 'people' || activePeopleTab !== 'followers' || followers.length === 0) return;

    const loadFollowerDetails = async () => {
      const currentFollowerIds = followers.map(f => f.follower_id).sort().join(',');
      const loadedFollowerIds = followersDetails.map(u => u.firebase_uid).sort().join(',');

      if (currentFollowerIds === loadedFollowerIds && followersDetails.length > 0) {
        return;
      }

      setLoadingFollowers(true);
      try {
        const userIds = followers.map(f => f.follower_id);
        const uniqueUserIds = [...new Set(userIds)];
        const userPromises = uniqueUserIds.map(id => getUser(id).catch(() => null));
        const users = await Promise.all(userPromises);
        setFollowersDetails(users.filter(u => u !== null));
      } catch (err) {
        console.error('Error loading follower details:', err);
      } finally {
        setLoadingFollowers(false);
      }
    };

    loadFollowerDetails();
  }, [activeTab, activePeopleTab, followers, currentUser]);

  useEffect(() => {
    if (!currentUser || activeTab !== 'people' || activePeopleTab !== 'following' || following.length === 0) return;

    const loadFollowingDetails = async () => {
      const currentFollowingIds = following.map(f => f.following_id).sort().join(',');
      const loadedFollowingIds = followingDetails.map(u => u.firebase_uid).sort().join(',');

      if (currentFollowingIds === loadedFollowingIds && followingDetails.length > 0) {
        return;
      }

      setLoadingFollowers(true);
      try {
        const userIds = following.map(f => f.following_id);
        const uniqueUserIds = [...new Set(userIds)];
        const userPromises = uniqueUserIds.map(id => getUser(id).catch(() => null));
        const users = await Promise.all(userPromises);
        setFollowingDetails(users.filter(u => u !== null));
      } catch (err) {
        console.error('Error loading following details:', err);
      } finally {
        setLoadingFollowers(false);
      }
    };

    loadFollowingDetails();
  }, [activeTab, activePeopleTab, following, currentUser]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    setError('');

    try {
      const users = await searchUsers(searchQuery);
      setSearchResults(users || []);
    } catch (err) {
      console.error('Error searching users:', err);
      setError('Failed to search users');
    } finally {
      setSearching(false);
    }
  };

  const handleFollow = async (userId) => {
    if (!currentUser) return;

    try {
      await followUser(currentUser.firebase_uid, userId);
      setSuccess('User followed successfully!');
      const followingData = await getFollowing(currentUser.firebase_uid);
      setFollowing(followingData || []);
      setFollowingDetails([]);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error following user:', err);
      setError('Failed to follow user');
    }
  };

  const handleOpenConversation = (conversation) => {
    setSelectedConversation(conversation);
    setActiveTab('chat');
  };

  const isFriend = (userId) => {
    const iFollowThem = following.some(f => f.following_id === userId);
    const theyFollowMe = followers.some(f => f.follower_id === userId);
    return iFollowThem && theyFollowMe;
  };

  const handleOpenChatWithUser = async (userId) => {
    if (!isFriend(userId)) {
      setError('You can only chat with users who follow you back (friends)');
      setTimeout(() => setError(''), 3000);
      return;
    }

    try {
      let conversation = conversations.find(conv =>
        conv.participants && conv.participants.includes(userId)
      );

      if (conversation) {
        handleOpenConversation(conversation);
      } else {
        const newConversation = await createConversation([currentUser.firebase_uid, userId]);
        setConversations(prev => [newConversation, ...prev]);
        handleOpenConversation(newConversation);
      }
    } catch (err) {
      console.error('Error opening conversation:', err);
      setError('Failed to start conversation');
    }
  };

  if (!currentUser) {
    return (
      <div className="ui-page">
        <div className="ui-container">
          <div className="ui-card">
            <EmptyState
              variant="card"
              title="Please sign in"
              description="You need to be signed in to access social features."
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
          <PageHeader
            title="Social"
            subtitle="Connect with travelers and share experiences"
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
          {activeTab !== 'chat' && (
            <div style={ {
              display: 'flex',
              gap: 8,
              marginBottom: activeTab === 'people' ? 16 : 32,
              backgroundColor: '#FAFBFC',
              padding: 8,
              borderRadius: 'var(--radius-lg)',
              border: '1px solid #E5E5E5',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={() => setActiveTab('feed')}
                style={ {
                  flex: 1,
                  minWidth: 140,
                  padding: '14px 24px',
                  border: 'none',
                  backgroundColor: activeTab === 'feed' ? '#FFFFFF' : 'transparent',
                  color: activeTab === 'feed' ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activeTab === 'feed' ? 700 : 500,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: activeTab === 'feed' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8
                }}
              >
                <FontAwesomeIcon icon={faStream} />
                Feed
              </button>

              <button
                onClick={() => setActiveTab('people')}
                style={ {
                  flex: 1,
                  minWidth: 140,
                  padding: '14px 24px',
                  border: 'none',
                  backgroundColor: activeTab === 'people' ? '#FFFFFF' : 'transparent',
                  color: activeTab === 'people' ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activeTab === 'people' ? 700 : 500,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: activeTab === 'people' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8
                }}
              >
                <FontAwesomeIcon icon={faUsers} />
                People
              </button>

              <button
                onClick={() => setActiveTab('conversations')}
                style={ {
                  flex: 1,
                  minWidth: 140,
                  padding: '14px 24px',
                  border: 'none',
                  backgroundColor: activeTab === 'conversations' ? '#FFFFFF' : 'transparent',
                  color: activeTab === 'conversations' ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activeTab === 'conversations' ? 700 : 500,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: activeTab === 'conversations' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  position: 'relative'
                }}
              >
                <FontAwesomeIcon icon={faComments} />
                Conversations
                {(() => {
                  const totalUnread = conversations.reduce((sum, conv) => sum + (conv.unread_count || 0), 0);
                  return totalUnread > 0 && (
                    <span style={ {
                      backgroundColor: '#E53E3E',
                      color: 'white',
                      borderRadius: '12px',
                      minWidth: 20,
                      height: 20,
                      padding: '0 6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      marginLeft: 4
                    }}>
                      {totalUnread}
                    </span>
                  );
                })()}
              </button>
            </div>
          )}

          {activeTab === 'people' && (
            <div style={ {
              display: 'flex',
              gap: 8,
              marginBottom: 32,
              backgroundColor: '#F5F5F5',
              padding: 6,
              borderRadius: 'var(--radius-md)',
              border: '1px solid #E5E5E5'
            }}>
              <button
                onClick={() => setActivePeopleTab('discover')}
                style={ {
                  flex: 1,
                  padding: '10px 16px',
                  border: 'none',
                  backgroundColor: activePeopleTab === 'discover' ? '#FFFFFF' : 'transparent',
                  color: activePeopleTab === 'discover' ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activePeopleTab === 'discover' ? 600 : 500,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-sm)',
                  boxShadow: activePeopleTab === 'discover' ? '0 1px 4px rgba(0,0,0,0.06)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                Discover
              </button>

              <button
                onClick={() => setActivePeopleTab('followers')}
                style={ {
                  flex: 1,
                  padding: '10px 16px',
                  border: 'none',
                  backgroundColor: activePeopleTab === 'followers' ? '#FFFFFF' : 'transparent',
                  color: activePeopleTab === 'followers' ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activePeopleTab === 'followers' ? 600 : 500,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-sm)',
                  boxShadow: activePeopleTab === 'followers' ? '0 1px 4px rgba(0,0,0,0.06)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                Followers
                {followers.length > 0 && (
                  <span style={ {
                    backgroundColor: '#E5E7EB',
                    color: 'var(--color-black)',
                    borderRadius: '10px',
                    minWidth: 18,
                    height: 18,
                    padding: '0 5px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    marginLeft: 6
                  }}>
                    {followers.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActivePeopleTab('following')}
                style={ {
                  flex: 1,
                  padding: '10px 16px',
                  border: 'none',
                  backgroundColor: activePeopleTab === 'following' ? '#FFFFFF' : 'transparent',
                  color: activePeopleTab === 'following' ? 'var(--color-black)' : 'var(--color-medium-gray)',
                  fontWeight: activePeopleTab === 'following' ? 600 : 500,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-sm)',
                  boxShadow: activePeopleTab === 'following' ? '0 1px 4px rgba(0,0,0,0.06)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                Following
                {following.length > 0 && (
                  <span style={ {
                    backgroundColor: '#E5E7EB',
                    color: 'var(--color-black)',
                    borderRadius: '10px',
                    minWidth: 18,
                    height: 18,
                    padding: '0 5px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    marginLeft: 6
                  }}>
                    {following.length}
                  </span>
                )}
              </button>
            </div>
          )}

          {}
          {activeTab === 'feed' && (
            <Feed currentUserId={currentUser.firebase_uid} />
          )}

          {activeTab === 'people' && activePeopleTab === 'discover' && (
            <div>
              {}
              <div style={ {
                marginBottom: 32,
                padding: 28,
                backgroundColor: '#FFFFFF',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid #F0F0F0',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
              }}>
                <h3 style={ {
                  fontSize: '1.2rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 16,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10
                }}>
                  <FontAwesomeIcon icon={faGlobe} />
                  Discover Travelers
                </h3>

                <div style={ {
                  display: 'flex',
                  gap: 12,
                  alignItems: 'center',
                  marginBottom: !searchQuery ? 24 : 0
                }}>
                  <div style={{ position: 'relative', flex: 1 }}>
                    <FontAwesomeIcon
                      icon={faSearch}
                      style={ {
                        position: 'absolute',
                        left: 18,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: 'var(--color-medium-gray)',
                        fontSize: '1rem'
                      }}
                    />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      placeholder="Search by name or username..."
                      style={ {
                        width: '100%',
                        padding: '16px 20px 16px 50px',
                        border: '2px solid #E5E5E5',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '1rem',
                        fontFamily: 'inherit',
                        backgroundColor: 'white',
                        transition: 'all 0.2s ease'
                      }}
                      onFocus={(e) => e.target.style.borderColor = 'var(--color-black)'}
                      onBlur={(e) => e.target.style.borderColor = '#E5E5E5'}
                    />
                  </div>
                  <button
                    onClick={handleSearch}
                    disabled={searching || !searchQuery.trim()}
                    style={ {
                      padding: '16px 32px',
                      backgroundColor: searching || !searchQuery.trim() ? '#E5E5E5' : 'var(--color-black)',
                      color: searching || !searchQuery.trim() ? 'var(--color-medium-gray)' : 'white',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      fontWeight: 600,
                      fontSize: '1rem',
                      cursor: searching || !searchQuery.trim() ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s ease',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8
                    }}
                  >
                    <FontAwesomeIcon icon={faSearch} />
                    {searching ? 'Searching...' : 'Search'}
                  </button>
                </div>

                {!searchQuery && (
                  <div style={ {
                    textAlign: 'center',
                    padding: 80,
                    backgroundColor: '#FAFBFC',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid #E5E5E5'
                  }}>
                    <div style={ {
                      width: 80,
                      height: 80,
                      backgroundColor: '#E5E7EB',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto 20px',
                      fontSize: '2rem',
                      color: '#9CA3AF'
                    }}>
                      <FontAwesomeIcon icon={faSearch} />
                    </div>
                    <p style={ {
                      fontSize: '1.2rem',
                      fontWeight: 600,
                      color: 'var(--color-black)',
                      marginBottom: 8
                    }}>
                      Find travelers
                    </p>
                    <p style={ {
                      fontSize: '0.95rem',
                      color: 'var(--color-light-gray)'
                    }}>
                      Search by name or username to connect with other travelers
                    </p>
                  </div>
                )}
              </div>

              {}
              {searchResults.length > 0 && (
                <div>
                  <h2 style={ {
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    color: 'var(--color-black)',
                    marginBottom: 16
                  }}>
                    Search Results ({searchResults.filter(u => u.firebase_uid !== currentUser.firebase_uid).length})
                  </h2>
                  <div style={ {
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                    gap: 20
                  }}>
                    {searchResults.map(user => (
                      <UserCard
                        key={user.id}
                        user={user}
                        currentUserId={currentUser.firebase_uid}
                        isFollowing={following.some(f => f.following_id === user.firebase_uid)}
                        isFriend={isFriend(user.firebase_uid)}
                        onFollow={() => handleFollow(user.firebase_uid)}
                        onOpenChat={() => handleOpenChatWithUser(user.firebase_uid)}
                      />
                    ))}
                  </div>
                  {searchResults.every(u => u.firebase_uid === currentUser.firebase_uid) && (
                    <div style={ {
                      textAlign: 'center',
                      padding: 60,
                      backgroundColor: '#FAFBFC',
                      borderRadius: 'var(--radius-lg)',
                      border: '1px solid #E5E5E5'
                    }}>
                      <div style={ {
                        width: 80,
                        height: 80,
                        backgroundColor: '#E5E7EB',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 20px',
                        fontSize: '2rem',
                        color: '#9CA3AF'
                      }}>
                        <FontAwesomeIcon icon={faUser} />
                      </div>
                      <p style={ {
                        fontSize: '1.2rem',
                        fontWeight: 600,
                        color: 'var(--color-black)',
                        marginBottom: 8
                      }}>
                        That's you!
                      </p>
                      <p style={ {
                        fontSize: '0.95rem',
                        color: 'var(--color-light-gray)'
                      }}>
                        You found yourself in the search. Try searching for other travelers.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {searchQuery && searchResults.length === 0 && !searching && (
                <div style={ {
                  textAlign: 'center',
                  padding: 80,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #E5E5E5'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    backgroundColor: '#E5E7EB',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    fontSize: '2rem',
                    color: '#9CA3AF'
                  }}>
                    <FontAwesomeIcon icon={faUsers} />
                  </div>
                  <p style={ {
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8
                  }}>
                    No users found
                  </p>
                  <p style={ {
                    fontSize: '0.95rem',
                    color: 'var(--color-light-gray)'
                  }}>
                    Try searching with a different name or username
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'people' && activePeopleTab === 'followers' && (
            <div>
              <h2 style={ {
                fontSize: '1.5rem',
                fontWeight: 700,
                color: 'var(--color-black)',
                marginBottom: 16,
                display: 'flex',
                alignItems: 'center',
                gap: 10
              }}>
                <FontAwesomeIcon icon={faUserFriends} />
                Your Followers ({followers.length})
              </h2>

              {loadingFollowers ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 60,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #E5E5E5'
                }}>
                  <p style={{ color: 'var(--color-medium-gray)' }}>Loading followers...</p>
                </div>
              ) : followersDetails.length > 0 ? (
                <div style={ {
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: 20
                }}>
                  {followersDetails.map(user => (
                    <UserCard
                      key={user.firebase_uid}
                      user={user}
                      currentUserId={currentUser.firebase_uid}
                      isFollowing={following.some(f => f.following_id === user.firebase_uid)}
                      isFriend={isFriend(user.firebase_uid)}
                      onFollow={() => handleFollow(user.firebase_uid)}
                      onOpenChat={() => handleOpenChatWithUser(user.firebase_uid)}
                    />
                  ))}
                </div>
              ) : (
                <div style={ {
                  textAlign: 'center',
                  padding: 80,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #E5E5E5'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    backgroundColor: '#E5E7EB',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    fontSize: '2rem',
                    color: '#9CA3AF'
                  }}>
                    <FontAwesomeIcon icon={faUserFriends} />
                  </div>
                  <p style={ {
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8
                  }}>
                    No followers yet
                  </p>
                  <p style={ {
                    fontSize: '0.95rem',
                    color: 'var(--color-light-gray)'
                  }}>
                    When people follow you, they will appear here
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'people' && activePeopleTab === 'following' && (
            <div>
              <h2 style={ {
                fontSize: '1.5rem',
                fontWeight: 700,
                color: 'var(--color-black)',
                marginBottom: 16,
                display: 'flex',
                alignItems: 'center',
                gap: 10
              }}>
                <FontAwesomeIcon icon={faUsers} />
                Following ({following.length})
              </h2>

              {loadingFollowers ? (
                <div style={ {
                  textAlign: 'center',
                  padding: 60,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #E5E5E5'
                }}>
                  <p style={{ color: 'var(--color-medium-gray)' }}>Loading...</p>
                </div>
              ) : followingDetails.length > 0 ? (
                <div style={ {
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: 20
                }}>
                  {followingDetails.map(user => (
                    <UserCard
                      key={user.firebase_uid}
                      user={user}
                      currentUserId={currentUser.firebase_uid}
                      isFollowing={true}
                      isFriend={isFriend(user.firebase_uid)}
                      onFollow={() => handleFollow(user.firebase_uid)}
                      onOpenChat={() => handleOpenChatWithUser(user.firebase_uid)}
                    />
                  ))}
                </div>
              ) : (
                <div style={ {
                  textAlign: 'center',
                  padding: 80,
                  backgroundColor: '#FAFBFC',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid #E5E5E5'
                }}>
                  <div style={ {
                    width: 80,
                    height: 80,
                    backgroundColor: '#E5E7EB',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    fontSize: '2rem',
                    color: '#9CA3AF'
                  }}>
                    <FontAwesomeIcon icon={faUsers} />
                  </div>
                  <p style={ {
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    color: 'var(--color-black)',
                    marginBottom: 8
                  }}>
                    Not following anyone
                  </p>
                  <p style={ {
                    fontSize: '0.95rem',
                    color: 'var(--color-light-gray)'
                  }}>
                    Start by searching for users and following them
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'conversations' && (
            <ConversationsList
              conversations={conversations}
              currentUserId={currentUser.firebase_uid}
              onOpenConversation={handleOpenConversation}
            />
          )}

          {activeTab === 'chat' && selectedConversation && (
            <ChatWindow
              conversation={selectedConversation}
              currentUserId={currentUser.firebase_uid}
              onBack={() => {
                setActiveTab('conversations');
                setSelectedConversation(null);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default Social;
