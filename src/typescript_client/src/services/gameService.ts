import { GameState, GameMode, GameSettings } from '../types/game';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

export const gameService = {
  async startGame(mode: GameMode, settings: GameSettings): Promise<{ gameId: string }> {
    const response = await fetch(`${API_URL}/game/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mode,
        settings
      })
    });

    if (!response.ok) {
      throw new Error('Failed to start game');
    }

    return response.json();
  },

  async getGameState(gameId: string): Promise<GameState> {
    const response = await fetch(`${API_URL}/game/${gameId}/state`);

    if (!response.ok) {
      throw new Error('Failed to get game state');
    }

    return response.json();
  },

  async move(gameId: string, direction: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ direction })
    });

    if (!response.ok) {
      throw new Error('Failed to move');
    }
  },

  async rotate(gameId: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/rotate`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to rotate');
    }
  },

  async drop(gameId: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/drop`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to drop');
    }
  },

  async hold(gameId: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/hold`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to hold');
    }
  },

  async castSpell(gameId: string, spellType: string, targetId?: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/spell`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        spellType,
        targetId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to cast spell');
    }
  },

  async pauseGame(gameId: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/pause`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to pause game');
    }
  },

  async resumeGame(gameId: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/resume`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to resume game');
    }
  },

  async endGame(gameId: string): Promise<void> {
    const response = await fetch(`${API_URL}/game/${gameId}/end`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to end game');
    }
  },

  getWebSocketUrl(gameId: string): string {
    return `${WS_URL}?gameId=${gameId}`;
  }
}; 