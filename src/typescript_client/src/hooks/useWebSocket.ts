import { useEffect, useRef, useCallback } from 'react';
import { GameState } from '../types/game';

interface UseWebSocketProps {
  url: string;
  onGameStateUpdate: (gameState: GameState) => void;
  onError: (error: string) => void;
  onClose: () => void;
}

export const useWebSocket = ({
  url,
  onGameStateUpdate,
  onError,
  onClose
}: UseWebSocketProps) => {
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    try {
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('WebSocket connection established');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'game_state') {
            onGameStateUpdate(data.game_state);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          onError('Failed to parse server message');
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError('WebSocket connection error');
      };

      socket.onclose = () => {
        console.log('WebSocket connection closed');
        onClose();
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      onError('Failed to establish WebSocket connection');
    }
  }, [url, onGameStateUpdate, onError, onClose]);

  const sendMessage = useCallback((message: any) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  return { sendMessage };
}; 