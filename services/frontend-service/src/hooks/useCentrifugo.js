import { useEffect, useRef, useState, useCallback } from 'react';
import { Centrifuge } from 'centrifuge';
import { getChatCentrifugoToken } from '../services/chat';
import { getSocialCentrifugoToken } from '../services/social';

export function useCentrifugo(channel, onMessage, service = 'chat') {
  const clientRef = useRef(null);
  const subRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const onMessageRef = useRef(onMessage);
  const serviceRef = useRef(service);
  const channelRef = useRef(channel);

  onMessageRef.current = onMessage;
  serviceRef.current = service;

  const disconnect = useCallback(() => {
    console.log('[Centrifugo] Disconnecting from', channelRef.current);

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (subRef.current) {
      console.log('[Centrifugo] Unsubscribing from channel:', channelRef.current);
      subRef.current.unsubscribe();
      subRef.current = null;
    }

    if (clientRef.current) {
      clientRef.current.disconnect();
      clientRef.current = null;
    }

    setConnected(false);
  }, []);

  const connect = useCallback(async () => {
    if (!channel) {
      console.log('[Centrifugo] No channel provided, skipping connection');
      return;
    }

    if (clientRef.current && channelRef.current === channel) {
      console.log('[Centrifugo] Already connected to', channel);
      return;
    }

    console.log('[Centrifugo] Setting up connection for channel:', channel);
    channelRef.current = channel;

    try {
      const currentService = serviceRef.current;
      const getTokenFn = currentService === 'social' ? getSocialCentrifugoToken : getChatCentrifugoToken;
      const response = await getTokenFn();

      const { token, ws_url } = response;
      const wsUrl = import.meta.env.VITE_CENTRIFUGO_WS_URL || ws_url;

      console.log('[Centrifugo] Connecting to', wsUrl);

      const centrifugeOptions = {
        token: token
      };
      const centrifuge = new Centrifuge(wsUrl, centrifugeOptions);

      centrifuge.on('connected', (ctx) => {
        console.log('[Centrifugo] Connected to', wsUrl, 'with client ID', ctx.clientId);
        setConnected(true);
        setError(null);
      });

      centrifuge.on('disconnected', (ctx) => {
        console.log('[Centrifugo] Disconnected from', wsUrl, 'reason:', ctx.reason);
        setConnected(false);
        clientRef.current = null;
        subRef.current = null;
      });

      centrifuge.on('error', (err) => {
        console.error('[Centrifugo] Error:', err);
        setError(err);
      });

      centrifuge.connect();

      const sub = centrifuge.newSubscription(channel);

      sub.on('publication', (ctx) => {
        console.log('[Centrifugo] Publication received on channel', channel, ':', ctx.data);
        onMessageRef.current && onMessageRef.current(ctx.data);
      });

      sub.on('subscribed', () => {
        console.log('[Centrifugo] Successfully subscribed to channel', channel);
      });

      sub.on('unsubscribed', () => {
        console.log('[Centrifugo] Unsubscribed from channel', channel);
      });

      sub.on('error', (err) => {
        console.error('[Centrifugo] Subscription error on channel', channel, ':', err);
      });

      console.log('[Centrifugo] Subscribing to channel', channel);
      sub.subscribe();

      clientRef.current = centrifuge;
      subRef.current = sub;

    } catch (err) {
      console.error('Failed to connect to Centrifugo:', err);
      setError(err);

      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    }
  }, [channel, disconnect]);

  useEffect(() => {
    if (!channel) {
      disconnect();
      return;
    }

    if (channel !== channelRef.current && clientRef.current) {
      console.log('[Centrifugo] Channel changed from', channelRef.current, 'to', channel);
      disconnect();
    }

    connect();

    return () => {
      disconnect();
    };
  }, [channel, connect, disconnect]);

  const publish = useCallback((data) => {
    if (subRef.current) {
      subRef.current.publish(data);
    }
  }, []);

  return {
    connected,
    error,
    publish
  };
}
