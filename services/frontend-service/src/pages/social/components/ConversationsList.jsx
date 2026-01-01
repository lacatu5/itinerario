import { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faComments, faUser, faCircle } from '@fortawesome/free-solid-svg-icons';
import { getUser } from '../../../services/users';
import { resolveImageUrl } from '../../../utils/url';

function ConversationsList({ conversations, currentUserId, onOpenConversation }) {
  const [conversationsWithUsers, setConversationsWithUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadConversationUsers = async () => {
      setLoading(true);
      try {
        const withUsers = await Promise.all(
          conversations.map(async (conv) => {
            try {
              const otherUserId = conv.participants?.find(id => id !== currentUserId);

              if (!otherUserId) {
                return { ...conv, otherUser: null };
              }

              const otherUser = await getUser(otherUserId);
              return { ...conv, otherUser };
            } catch (err) {
              console.error('Error loading conversation user:', err);
              return { ...conv, otherUser: null };
            }
          })
        );
        setConversationsWithUsers(withUsers.filter(c => c.otherUser));
      } catch (err) {
        console.error('Error loading conversations:', err);
      } finally {
        setLoading(false);
      }
    };

    if (conversations.length > 0) {
      loadConversationUsers();
    } else {
      setLoading(false);
    }
  }, [conversations, currentUserId]);

  if (loading) {
    return (
      <div style={ {
        textAlign: 'center',
        padding: 60,
        backgroundColor: '#FAFBFC',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid #E5E5E5'
      }}>
        <p style={{ color: 'var(--color-medium-gray)' }}>Loading conversations...</p>
      </div>
    );
  }

  if (conversationsWithUsers.length === 0) {
    return (
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
          <FontAwesomeIcon icon={faComments} />
          Your Conversations (0)
        </h2>
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
            <FontAwesomeIcon icon={faComments} />
          </div>
          <p style={ {
            fontSize: '1.2rem',
            fontWeight: 600,
            color: 'var(--color-black)',
            marginBottom: 8
          }}>
            No conversations yet
          </p>
          <p style={ {
            fontSize: '0.95rem',
            color: 'var(--color-light-gray)'
          }}>
            Start by following travelers to connect and chat
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h2 style={ {
        fontSize: '1.5rem',
        fontWeight: 700,
        color: 'var(--color-black)',
        marginBottom: 20,
        display: 'flex',
        alignItems: 'center',
        gap: 10
      }}>
        <FontAwesomeIcon icon={faComments} />
        Your Conversations ({conversationsWithUsers.length})
      </h2>

      <div style={ {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: 20
      }}>
        {conversationsWithUsers.map((conv) => (
          <div
            key={conv.id}
            onClick={() => onOpenConversation(conv)}
            style={ {
              padding: 20,
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid #F0F0F0',
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
            }}
          >
            {}
            <div style={ {
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              marginBottom: 12
            }}>
              {conv.otherUser?.profile_image_url ? (
                <img
                  src={resolveImageUrl(conv.otherUser.profile_image_url)}
                  alt={conv.otherUser.name}
                  style={ {
                    width: 56,
                    height: 56,
                    objectFit: 'cover',
                    borderRadius: '50%',
                    border: '2px solid #F0F0F0'
                  }}
                />
              ) : (
                <div style={ {
                  width: 56,
                  height: 56,
                  backgroundColor: '#E5E7EB',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#6B7280',
                  fontSize: '1.3rem'
                }}>
                  <FontAwesomeIcon icon={faUser} />
                </div>
              )}

              <div style={{ flex: 1, minWidth: 0 }}>
                <h3 style={ {
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  color: 'var(--color-black)',
                  marginBottom: 4,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {conv.otherUser?.name}
                </h3>
                {conv.otherUser?.username && (
                  <p style={ {
                    color: 'var(--color-medium-gray)',
                    fontSize: '0.9rem',
                    margin: 0,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    @{conv.otherUser.username}
                  </p>
                )}
              </div>

              {}
              <div style={ {
                width: 10,
                height: 10,
                backgroundColor: '#10B981',
                borderRadius: '50%',
                border: '2px solid white',
                boxShadow: '0 0 0 1px rgba(16, 185, 129, 0.3)'
              }}
              title="Active"
              />
            </div>

            {}
            {conv.last_message_preview && (
              <div style={ {
                padding: 12,
                backgroundColor: '#FAFBFC',
                borderRadius: 'var(--radius-md)',
                border: '1px solid #E5E5E5',
                marginBottom: 12
              }}>
                <p style={ {
                  color: 'var(--color-medium-gray)',
                  fontSize: '0.9rem',
                  lineHeight: 1.4,
                  margin: 0,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {conv.last_message_preview}
                </p>
              </div>
            )}

            {}
            {conv.last_message_at && (
              <div style={ {
                color: 'var(--color-light-gray)',
                fontSize: '0.85rem',
                textAlign: 'right'
              }}>
                {new Date(conv.last_message_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            )}

            {}
            {conv.unread_count > 0 && (
              <div style={ {
                position: 'absolute',
                top: 12,
                right: 12,
                minWidth: 24,
                height: 24,
                padding: '0 8px',
                backgroundColor: '#E53E3E',
                color: 'white',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                fontWeight: 700
              }}>
                {conv.unread_count}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ConversationsList;
