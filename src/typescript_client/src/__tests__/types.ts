import { GameMode, GameSettings, Player, GameState, SpellType, Block, Tetromino, TetrominoType } from '../types/game';

export const mockBlock: Block = {
  id: '1',
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
    { id: '1', x: 0, y: 0, type: TetrominoType.I, color: '#00f0f0' },
    { id: '2', x: 1, y: 0, type: TetrominoType.I, color: '#00f0f0' },
    { id: '3', x: 2, y: 0, type: TetrominoType.I, color: '#00f0f0' },
    { id: '4', x: 3, y: 0, type: TetrominoType.I, color: '#00f0f0' }
  ]
};

export const mockGameSettings: GameSettings = {
  difficulty: 'MEDIUM',
  speed: 1,
  gravity: 1,
  musicVolume: 0.5,
  soundVolume: 0.5,
  controls: {
    moveLeft: 'ArrowLeft',
    moveRight: 'ArrowRight',
    rotate: 'ArrowUp',
    drop: 'Space',
    hold: 'c'
  }
};

export const mockPlayer: Player = {
  id: 'player1',
  name: 'Player 1',
  score: 0,
  health: 100,
  currentTetromino: mockTetromino,
  nextTetrominos: [mockTetromino],
  heldTetromino: null,
  spells: [SpellType.CLEAR_LINE],
  towerBlocks: [mockBlock]
};

export const mockGameState: GameState = {
  gameMode: GameMode.RACE,
  players: {
    player1: mockPlayer
  },
  score: 0,
  level: 1,
  linesCleared: 0,
  timer: 0,
  isGameOver: false
};

export const mockSpell = {
  type: SpellType.CLEAR_LINE,
  targetId: 'player2'
}; 