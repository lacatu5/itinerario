import { useState, useEffect, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faArrowLeft,
  faPaperPlane,
  faUser,
  faCircle,
  faSmile
} from '@fortawesome/free-solid-svg-icons';
import { getMessages, sendMessage } from '../../../services/chat';
import { getUser } from '../../../services/users';
import { resolveImageUrl } from '../../../utils/url';
import { useCentrifugo } from '../../../hooks/useCentrifugo';

function ChatWindow({ conversation, currentUserId, onBack }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [otherUser, setOtherUser] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const loadOtherUser = async () => {
      try {
        const otherUserId = conversation.participants?.find(id => id !== currentUserId);
        if (otherUserId) {
          const user = await getUser(otherUserId);
          setOtherUser(user);
        }
      } catch (err) {
        console.error('Error loading other user:', err);
      }
    };

    loadOtherUser();
  }, [conversation, currentUserId]);

  useEffect(() => {
    const loadMessages = async () => {
      setLoading(true);
      try {
        const msgs = await getMessages(conversation.id);
        setMessages(msgs);
      } catch (err) {
        console.error('Error loading messages:', err);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, [conversation.id]);

  useCentrifugo('chat:' + conversation.id, (message) => {
    setMessages(prev => {
      const exists = prev.some(m => m.id === message.id);
      if (exists) return prev;
      return [...prev, message];
    });
  }, 'chat');

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!newMessage.trim() || sending) return;

    const messageText = newMessage.trim();
    setNewMessage('');
    setSending(true);

    try {
      await sendMessage(conversation.id, messageText);
    } catch (err) {
      console.error('Error sending message:', err);
      setNewMessage(messageText);
    } finally {
      setSending(false);
    }
  };

  const formatMessageTime = (timestamp) => {
    if (!timestamp) return '';

    const date = new Date(timestamp);

    if (isNaN(date.getTime())) {
      const safariCompatible = new Date(timestamp.replace(' ', 'T'));
      if (!isNaN(safariCompatible.getTime())) {
        return safariCompatible.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        });
      }
      return '';
    }

    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();

    if (isToday) {
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  return (
    <div style={ {
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 200px)',
      backgroundColor: '#FFFFFF',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #F0F0F0',
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      overflow: 'hidden'
    }}>
      <div style={ {
        padding: '20px 24px',
        borderBottom: '1px solid #F0F0F0',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        backgroundColor: '#FAFBFC'
      }}>
        <button
          onClick={onBack}
          style={ {
            padding: '8px 12px',
            backgroundColor: 'transparent',
            border: 'none',
            color: 'var(--color-medium-gray)',
            cursor: 'pointer',
            fontSize: '1.2rem',
            display: 'flex',
            alignItems: 'center',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-black)'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-medium-gray)'}
        >
          <FontAwesomeIcon icon={faArrowLeft} />
        </button>

        {otherUser?.profile_image_url ? (
          <img
            src={resolveImageUrl(otherUser.profile_image_url)}
            alt={otherUser.name}
            style={ {
              width: 44,
              height: 44,
              objectFit: 'cover',
              borderRadius: '50%',
              border: '2px solid #F0F0F0'
            }}
          />
        ) : (
          <div style={ {
            width: 44,
            height: 44,
            backgroundColor: '#E5E7EB',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6B7280',
            fontSize: '1.2rem'
          }}>
            <FontAwesomeIcon icon={faUser} />
          </div>
        )}

        <div style={{ flex: 1 }}>
          <h3 style={ {
            fontSize: '1.1rem',
            fontWeight: 700,
            color: 'var(--color-black)',
            marginBottom: 2
          }}>
            {otherUser?.name || 'Loading...'}
          </h3>
          <div style={ {
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            color: 'var(--color-light-gray)',
            fontSize: '0.85rem'
          }}>
            <FontAwesomeIcon icon={faCircle} style={{ fontSize: '0.5rem', color: '#10B981' }} />
            Active now
          </div>
        </div>
      </div>

      {}
      <div style={ {
        flex: 1,
        overflowY: 'auto',
        padding: 24,
        backgroundColor: '#FFFFFF',
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }}>
        {loading ? (
          <div style={ {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            color: 'var(--color-light-gray)'
          }}>
            <p>Loading messages...</p>
          </div>
        ) : messages.length === 0 ? (
          <div style={ {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            textAlign: 'center',
            color: 'var(--color-light-gray)'
          }}>
            <div>
              <FontAwesomeIcon icon={faSmile} style={{ fontSize: '3rem', marginBottom: 16, opacity: 0.5 }} />
              <p style={{ fontSize: '1rem', fontWeight: 500 }}>Start the conversation!</p>
              <p style={{ fontSize: '0.9rem' }}>Send your first message below</p>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => {
            const senderId = msg.sender_id || msg.senderId || msg.user_id;
            const isOwnMessage = String(senderId) === String(currentUserId);
            const showAvatar = index === 0 || messages[index - 1].sender_id !== msg.sender_id;

            return (
              <div
                key={msg.id}
                style={ {
                  display: 'flex',
                  justifyContent: isOwnMessage ? 'flex-end' : 'flex-start',
                  alignItems: 'flex-end',
                  gap: 8
                }}
              >
                {!isOwnMessage && (
                  <div style={{ width: 32, height: 32, flexShrink: 0 }}>
                    {showAvatar && (
                      otherUser?.profile_image_url ? (
                        <img
                          src={resolveImageUrl(otherUser.profile_image_url)}
                          alt={otherUser.name}
                          style={ {
                            width: 32,
                            height: 32,
                            objectFit: 'cover',
                            borderRadius: '50%'
                          }}
                        />
                      ) : (
                        <div style={ {
                          width: 32,
                          height: 32,
                          backgroundColor: '#E5E7EB',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#6B7280',
                          fontSize: '0.9rem'
                        }}>
                          <FontAwesomeIcon icon={faUser} />
                        </div>
                      )
                    )}
                  </div>
                )}

                <div style={ {
                  maxWidth: '70%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isOwnMessage ? 'flex-end' : 'flex-start'
                }}>
                  <div style={ {
                    padding: '12px 16px',
                    backgroundColor: isOwnMessage ? 'var(--color-black)' : '#F0F0F0',
                    color: isOwnMessage ? 'white' : 'var(--color-black)',
                    borderRadius: isOwnMessage
                      ? 'var(--radius-lg) var(--radius-lg) 4px var(--radius-lg)'
                      : 'var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px',
                    wordWrap: 'break-word',
                    wordBreak: 'break-word'
                  }}>
                    <p style={ {
                      margin: 0,
                      fontSize: '0.95rem',
                      lineHeight: 1.4
                    }}>
                      {msg.content}
                    </p>
                  </div>
                  <span style={ {
                    fontSize: '0.75rem',
                    color: 'var(--color-light-gray)',
                    marginTop: 4,
                    paddingInline: 4
                  }}>
                    {formatMessageTime(msg.created_at)}
                  </span>
                </div>

                {isOwnMessage && <div style={{ width: 32 }} />}
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {}
      <form
        onSubmit={handleSendMessage}
        style={ {
          padding: 20,
          borderTop: '1px solid #F0F0F0',
          backgroundColor: '#FAFBFC'
        }}
      >
        <div style={ {
          display: 'flex',
          gap: 12,
          alignItems: 'flex-end'
        }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(e);
                }
              }}
              placeholder="Type a message..."
              rows={1}
              style={ {
                width: '100%',
                padding: '12px 16px',
                border: '1px solid #E5E5E5',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.95rem',
                fontFamily: 'inherit',
                resize: 'none',
                minHeight: 48,
                maxHeight: 120
              }}
              disabled={sending}
            />
          </div>

          <button
            type="submit"
            disabled={!newMessage.trim() || sending}
            style={ {
              padding: '12px 24px',
              backgroundColor: !newMessage.trim() || sending ? '#E5E5E5' : 'var(--color-black)',
              color: !newMessage.trim() || sending ? 'var(--color-medium-gray)' : 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              cursor: !newMessage.trim() || sending ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: '0.95rem',
              transition: 'all 0.2s ease',
              height: 48
            }}
          >
            <FontAwesomeIcon icon={faPaperPlane} />
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatWindow;
