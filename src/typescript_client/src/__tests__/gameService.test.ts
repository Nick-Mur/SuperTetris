import { gameService } from '../services/gameService';
import { GameMode, GameSettings } from '../types/game';

describe('gameService', () => {
  const mockGameId = 'test-game-id';
  const mockSettings: GameSettings = {
    difficulty: 'MEDIUM',
    speed: 1.0,
    gravity: 1,
    musicVolume: 0.5,
    soundVolume: 0.5,
    controls: {
      moveLeft: 'ArrowLeft',
      moveRight: 'ArrowRight',
      rotate: 'ArrowUp',
      drop: 'ArrowDown',
      hold: 'c',
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  it('starts a game', async () => {
    const mockResponse = { gameId: mockGameId };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await gameService.startGame(GameMode.RACE, mockSettings);
    expect(result).toBe(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith('/api/game/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mode: GameMode.RACE,
        settings: mockSettings,
      }),
    });
  });

  it('gets game state', async () => {
    const mockGameState = {
      id: mockGameId,
      status: 'playing',
      players: [],
    };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockGameState),
    });

    const result = await gameService.getGameState(mockGameId);
    expect(result).toEqual(mockGameState);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/state`);
  });

  it('sends move command', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.move(mockGameId, 'left');
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ direction: 'left' }),
    });
  });

  it('sends rotate command', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.rotate(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/rotate`, {
      method: 'POST',
    });
  });

  it('sends drop command', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.drop(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/drop`, {
      method: 'POST',
    });
  });

  it('sends hold command', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.hold(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/hold`, {
      method: 'POST',
    });
  });

  it('sends spell cast command', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.castSpell(mockGameId, 'fireball', 'player2');
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/spell`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        spellType: 'fireball',
        targetId: 'player2',
      }),
    });
  });

  it('pauses game', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.pauseGame(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/pause`, {
      method: 'POST',
    });
  });

  it('resumes game', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.resumeGame(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/resume`, {
      method: 'POST',
    });
  });

  it('ends game', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
    });

    await gameService.endGame(mockGameId);
    expect(global.fetch).toHaveBeenCalledWith(`/api/game/${mockGameId}/end`, {
      method: 'POST',
    });
  });

  it('gets WebSocket URL', () => {
    const wsUrl = gameService.getWebSocketUrl(mockGameId);
    expect(wsUrl).toBe(`ws://localhost:8080/ws/game/${mockGameId}`);
  });

  it('handles API errors', async () => {
    const mockError = new Error('API Error');
    (global.fetch as jest.Mock).mockRejectedValueOnce(mockError);

    await expect(gameService.startGame(GameMode.RACE, mockSettings)).rejects.toThrow(
      'API Error'
    );
  });
}); 