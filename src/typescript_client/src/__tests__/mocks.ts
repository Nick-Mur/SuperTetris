import { GameMode, GameSettings, GameState, Player, TetrominoType, SpellType, Block, Tetromino } from '../types/game';

declare global {
  interface Window {
    WebSocket: typeof WebSocket;
    fetch: typeof fetch;
    ResizeObserver: typeof ResizeObserver;
    requestAnimationFrame: typeof requestAnimationFrame;
    cancelAnimationFrame: typeof cancelAnimationFrame;
  }
}

// Моки для тестов
export const mockBlock: Block = {
  id: 'block-1',
  x: 0,
  y: 0,
  type: TetrominoType.I,
  color: '#00f0f0'
};

export const mockTetromino: Tetromino = {
  type: TetrominoType.I,
  x: 3,
  y: 0,
  rotation: 0,
  blocks: [
    { id: 'block-I-0', x: 3, y: 0, type: TetrominoType.I, color: '#00f0f0' },
    { id: 'block-I-1', x: 4, y: 0, type: TetrominoType.I, color: '#00f0f0' },
    { id: 'block-I-2', x: 5, y: 0, type: TetrominoType.I, color: '#00f0f0' },
    { id: 'block-I-3', x: 6, y: 0, type: TetrominoType.I, color: '#00f0f0' },
  ]
};

export const mockGameSettings: GameSettings = {
  difficulty: 'MEDIUM',
  speed: 1.0,
  gravity: 9.8,
  musicVolume: 0.5,
  soundVolume: 0.5,
  controls: {
    moveLeft: 'ArrowLeft',
    moveRight: 'ArrowRight',
    rotate: 'ArrowUp',
    drop: 'ArrowDown',
    hold: 'c'
  }
};

export const mockPlayer: Player = {
  id: 'player-1',
  name: 'Player 1',
  score: 0,
  health: 100,
  currentTetromino: mockTetromino,
  nextTetrominos: [mockTetromino],
  heldTetromino: null,
  spells: [SpellType.CLEAR_LINE, SpellType.ADD_BLOCKS],
  towerBlocks: []
};

export const mockGameState: GameState = {
  gameMode: GameMode.SINGLE_PLAYER,
  players: {
    'player-1': mockPlayer
  },
  score: 0,
  level: 1,
  linesCleared: 0,
  timer: 0,
  isGameOver: false
};

export const mockSpell: SpellType = SpellType.CLEAR_LINE;

// Моки для WebSocket
class MockWebSocketClass {
  send = jest.fn();
  close = jest.fn();
  addEventListener = jest.fn();
  removeEventListener = jest.fn();
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
}

export const mockWebSocket = new MockWebSocketClass();

export const mockFetch = jest.fn();

export const mockRequestAnimationFrame = jest.fn((callback: FrameRequestCallback) => {
  setTimeout(() => callback(performance.now()), 0);
  return 1;
});

export const mockCancelAnimationFrame = jest.fn((id: number) => {
  clearTimeout(id);
});

export const setupMocks = () => {
  window.WebSocket = MockWebSocketClass as any;
  window.fetch = mockFetch as any;
  window.requestAnimationFrame = mockRequestAnimationFrame as any;
  window.cancelAnimationFrame = mockCancelAnimationFrame as any;
};

export const clearMocks = () => {
  jest.clearAllMocks();
  mockWebSocket.send.mockClear();
  mockWebSocket.close.mockClear();
  mockWebSocket.addEventListener.mockClear();
  mockWebSocket.removeEventListener.mockClear();
  mockFetch.mockClear();
  mockRequestAnimationFrame.mockClear();
  mockCancelAnimationFrame.mockClear();
}; 