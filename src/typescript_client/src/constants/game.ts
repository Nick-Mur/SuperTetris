import { TetrominoType, SpellType, GameSettings } from '../types/game';

export const TETROMINO_COLORS: Record<TetrominoType, string> = {
  [TetrominoType.I]: '#00f0f0',
  [TetrominoType.J]: '#0000f0',
  [TetrominoType.L]: '#f0a000',
  [TetrominoType.O]: '#f0f000',
  [TetrominoType.S]: '#00f000',
  [TetrominoType.T]: '#a000f0',
  [TetrominoType.Z]: '#f00000'
};

export const TETROMINO_SHAPES: Record<TetrominoType, [number, number][]> = {
  [TetrominoType.I]: [
    [0, 0],
    [-1, 0],
    [1, 0],
    [2, 0]
  ],
  [TetrominoType.J]: [
    [0, 0],
    [-1, 0],
    [1, 0],
    [1, 1]
  ],
  [TetrominoType.L]: [
    [0, 0],
    [-1, 0],
    [1, 0],
    [-1, 1]
  ],
  [TetrominoType.O]: [
    [0, 0],
    [1, 0],
    [0, 1],
    [1, 1]
  ],
  [TetrominoType.S]: [
    [0, 0],
    [-1, 0],
    [0, 1],
    [1, 1]
  ],
  [TetrominoType.T]: [
    [0, 0],
    [-1, 0],
    [1, 0],
    [0, 1]
  ],
  [TetrominoType.Z]: [
    [0, 0],
    [1, 0],
    [0, 1],
    [-1, 1]
  ]
};

export const SPELL_ICONS: Record<SpellType, string> = {
  [SpellType.CLEAR_LINE]: '🗑️',
  [SpellType.SWAP_PIECES]: '🔄',
  [SpellType.SLOW_DOWN]: '⏱️',
  [SpellType.SPEED_UP]: '⚡',
  [SpellType.ADD_BLOCKS]: '➕',
  [SpellType.REMOVE_BLOCKS]: '➖'
};

export const DEFAULT_GAME_SETTINGS: GameSettings = {
  difficulty: 'MEDIUM',
  speed: 1,
  gravity: 1,
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