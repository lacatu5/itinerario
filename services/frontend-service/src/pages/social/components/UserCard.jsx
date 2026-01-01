import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserPlus, faEnvelope, faUser, faCheck, faComments, faUserCheck } from '@fortawesome/free-solid-svg-icons';
import { resolveImageUrl } from '../../../utils/url';

function UserCard({ user, currentUserId, isFollowing, isFriend, onFollow, onOpenChat }) {
  if (user.id === currentUserId) {
    return null;
  }

  return (
    <div style={ {
      padding: 20,
      backgroundColor: '#FFFFFF',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #F0F0F0',
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      transition: 'all 0.3s ease',
      position: 'relative'
    }}>
      {}
      <div style={ {
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        marginBottom: 16
      }}>
        {user.profile_image_url ? (
          <img
            src={resolveImageUrl(user.profile_image_url)}
            alt={user.name}
            style={ {
              width: 60,
              height: 60,
              objectFit: 'cover',
              borderRadius: '50%',
              border: '2px solid #F0F0F0'
            }}
          />
        ) : (
          <div style={ {
            width: 60,
            height: 60,
            backgroundColor: '#E5E7EB',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6B7280',
            fontSize: '1.5rem'
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
            {user.name}
          </h3>
          {user.username && (
            <p style={ {
              color: 'var(--color-medium-gray)',
              fontSize: '0.9rem',
              margin: 0,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              @{user.username}
            </p>
          )}
        </div>
      </div>

      {}
      <div style={ {
        display: 'flex',
        gap: 8
      }}>
        {isFollowing ? (
          <>
            <button
              disabled
              style={ {
                flex: 1,
                padding: '10px 16px',
                backgroundColor: '#F0F0F0',
                color: 'var(--color-medium-gray)',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'default',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                transition: 'all 0.2s ease'
              }}
            >
              <FontAwesomeIcon icon={faCheck} />
              Following
            </button>

            {isFriend && (
              <button
                onClick={onOpenChat}
                style={ {
                  flex: 1,
                  padding: '10px 16px',
                  backgroundColor: 'var(--color-black)',
                  color: 'white',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  transition: 'all 0.2s ease'
                }}
              >
                <FontAwesomeIcon icon={faComments} />
                Chat
              </button>
            )}
          </>
        ) : (
          <button
            onClick={onFollow}
            style={ {
              flex: 1,
              padding: '10px 16px',
              backgroundColor: 'var(--color-black)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              transition: 'all 0.2s ease'
            }}
          >
            <FontAwesomeIcon icon={faUserPlus} />
            Follow
          </button>
        )}
      </div>
    </div>
  );
}

export default UserCard;
