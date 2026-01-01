import { useState, useEffect, useCallback } from 'react';
import {
  likeItinerary,
  unlikeItinerary,
  updateLikeComment,
  getItineraryLikes,
  getItineraryStats,
  checkLikeStatus
} from '../services/likes';
import { getCurrentUser } from '../services/authStore';
import '../styles/itinerary-ui.css';
import { resolveImageUrl } from '../utils/url';

function LikesAndComments({ itineraryId, ownerId, onStatsChange }) {
  const [stats, setStats] = useState({ like_count: 0 });
  const [likes, setLikes] = useState([]);
  const [userLikeStatus, setUserLikeStatus] = useState(null);
  const [showComments, setShowComments] = useState(false);
  const [loading, setLoading] = useState(true);
  const [commenting, setCommenting] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [error, setError] = useState('');
  const [commentsLoading, setCommentsLoading] = useState(false);

  const currentUser = getCurrentUser();
  const currentUserId = currentUser?.id ?? null;
  const canInteract = currentUser && currentUser.id !== ownerId;

  const getDisplayName = useCallback((like) => {
    return like?.user?.name || like?.user_name || 'Anonymous';
  }, []);

  const getProfileImage = useCallback((like) => {
    return like?.user?.profile_image_url || like?.user_profile_image_url || null;
  }, []);

  const getUsername = useCallback((like) => {
    return like?.user?.username || like?.user_username || null;
  }, []);

  const getInitial = useCallback((like) => {
    const username = getUsername(like);
    if (username) return username.charAt(0).toUpperCase();
    const name = getDisplayName(like);
    if (name) return name.charAt(0).toUpperCase();
    return '?';
  }, [getUsername, getDisplayName]);

  const loadComments = useCallback(async () => {
    setCommentsLoading(true);
    try {
      const likesData = await getItineraryLikes(itineraryId);
      setLikes(likesData || []);
      return likesData || [];
    } catch (e) {
      setError(e.message || 'Failed to load comments');
      throw e;
    } finally {
      setCommentsLoading(false);
    }
  }, [itineraryId]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const statsData = await getItineraryStats(itineraryId);
      setStats(statsData);
      if (onStatsChange) {
        onStatsChange(statsData?.like_count ?? 0);
      }

      try {
        await loadComments();
      } catch (e) {
      }

      try {
        const likeStatus = await checkLikeStatus(itineraryId);
        setUserLikeStatus(likeStatus);
        if (likeStatus.liked) {
          setCommentText(likeStatus.comment || '');
        } else {
          setCommentText('');
        }
      } catch (e) {
        setUserLikeStatus({ liked: false });
        setCommentText('');
      }
    } catch (e) {
      setError('Failed to load likes data');
    } finally {
      setLoading(false);
    }
  }, [itineraryId, currentUserId, loadComments]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleLike = async () => {
    if (!currentUser) return;

    try {
      setError('');

      if (userLikeStatus?.liked) {
        await unlikeItinerary(itineraryId);
        setUserLikeStatus({ liked: false });
        const newCount = Math.max(0, (stats.like_count ?? 0) - 1);
        setStats(prev => ({ ...prev, like_count: newCount }));
        if (onStatsChange) onStatsChange(newCount);
        setCommentText('');
      } else {
        await likeItinerary(itineraryId, commentText);
        setUserLikeStatus({ liked: true, comment: commentText });
        const newCount = (stats.like_count ?? 0) + 1;
        setStats(prev => ({ ...prev, like_count: newCount }));
        if (onStatsChange) onStatsChange(newCount);
      }
    } catch (e) {
      setError(e.message || 'Failed to update like');
    }
  };

  const handleCommentUpdate = async () => {
    if (!currentUser || !userLikeStatus?.liked) return;

    try {
      setCommenting(true);
      setError('');

      await updateLikeComment(itineraryId, commentText);
      setUserLikeStatus(prev => ({ ...prev, comment: commentText }));

      await loadComments().catch(() => {});
    } catch (e) {
      setError(e.message || 'Failed to update comment');
    } finally {
      setCommenting(false);
    }
  };

  const handleShowComments = async () => {
    if (!showComments) {
      await loadComments().catch(() => {});
    }
    setShowComments(!showComments);
  };

  const displayComments = likes.filter((like) => like.comment && like.comment.trim());
  const canToggleComments = stats.like_count > 0 || displayComments.length > 0 || commentsLoading;

  if (loading) {
    return <div className="ui-help">Loading likes...</div>;
  }

  return (
    <div style={ {
      marginTop: 24,
      padding: 24,
      backgroundColor: '#FFFFFF',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #F0F0F0',
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 18, color: 'var(--color-primary)' }}>♡</span>
          <span className="ui-help">
            {stats.like_count} {stats.like_count === 1 ? 'like' : 'likes'}
          </span>
        </div>

        {canInteract && (
          <button
            onClick={handleLike}
            className={`ui-button ui-button-sm ${userLikeStatus?.liked ? 'ui-button-danger' : ''}`}
          >
            {userLikeStatus?.liked ? 'Unlike' : 'Like'}
          </button>
        )}

        {canToggleComments && (
          <button
            onClick={handleShowComments}
            className="ui-button ui-button-sm ui-button-outline"
          >
            {showComments ? 'Hide Comments' : `Show Comments${displayComments.length ? ` (${displayComments.length})` : ''}`}
          </button>
        )}
      </div>

      {}
      {canInteract && userLikeStatus?.liked && (
        <div style={{ marginBottom: 16 }}>
          <label className="ui-label">Your comment (optional)</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Add a comment about this trip..."
              className="ui-input"
              rows={2}
              style={{ flex: 1 }}
            />
            <button
              onClick={handleCommentUpdate}
              disabled={commenting}
              className="ui-button ui-button-sm"
            >
              {commenting ? 'Saving...' : 'Update'}
            </button>
          </div>
        </div>
      )}

      {}
      {error && (
        <div style={{ color: 'var(--color-black)', fontSize: 14, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {}
      {showComments && (
        <div>
          <h4 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>Comments</h4>
          {commentsLoading ? (
            <p className="ui-help">Loading comments...</p>
          ) : displayComments.length === 0 ? (
            <p className="ui-help">No comments yet.</p>
          ) : (
            <div style={{ display: 'grid', gap: 12 }}>
              {displayComments.map((like) => (
                <div
                  key={like.id}
                  style={ {
                    background: 'white',
                    padding: 12,
                    borderRadius: 6,
                    border: '1px solid #e0e0e0'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={ {
                        width: 34,
                        height: 34,
                        borderRadius: '50%',
                        overflow: 'hidden',
                        flexShrink: 0,
                        boxShadow: '0 0 0 2px rgba(0, 0, 0, 0.06)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        {getProfileImage(like) ? (
                          <img
                            src={resolveImageUrl(getProfileImage(like))}
                            alt={getDisplayName(like)}
                            style={ {
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                              borderRadius: '50%'
                            }}
                          />
                        ) : (
                          <div
                            style={ {
                              width: '100%',
                              height: '100%',
                              borderRadius: '50%',
                              background: 'linear-gradient(135deg, #e8e8e8 0%, #d4d4d4 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 13,
                              fontWeight: 700,
                              color: '#666',
                              textTransform: 'uppercase'
                            }}
                          >
                            {getInitial(like)}
                          </div>
                        )}
                      </div>
                      <strong style={{ fontSize: 14, color: '#333' }}>
                        {getDisplayName(like)}
                      </strong>
                    </div>
                    <span className="ui-help" style={{ fontSize: 12 }}>
                      {new Date(like.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p style={{ margin: 0, lineHeight: 1.4, fontSize: 14 }}>
                    {like.comment}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default LikesAndComments;
