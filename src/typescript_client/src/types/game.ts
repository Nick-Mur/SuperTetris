export enum TetrominoType {
  I = 'I',
  J = 'J',
  L = 'L',
  O = 'O',
  S = 'S',
  T = 'T',
  Z = 'Z'
}

export enum Direction {
  UP = 'UP',
  DOWN = 'DOWN',
  LEFT = 'LEFT',
  RIGHT = 'RIGHT',
}

export enum RotationDirection {
  CLOCKWISE = 'CLOCKWISE',
  COUNTER_CLOCKWISE = 'COUNTER_CLOCKWISE',
}

export enum SpellType {
  CLEAR_LINE = 'CLEAR_LINE',
  SWAP_PIECES = 'SWAP_PIECES',
  SLOW_DOWN = 'SLOW_DOWN',
  SPEED_UP = 'SPEED_UP',
  ADD_BLOCKS = 'ADD_BLOCKS',
  REMOVE_BLOCKS = 'REMOVE_BLOCKS'
}

export enum GameMode {
  SINGLE_PLAYER = 'SINGLE_PLAYER',
  MULTIPLAYER = 'MULTIPLAYER',
  RACE = 'RACE',
  SURVIVAL = 'SURVIVAL',
  PUZZLE = 'PUZZLE'
}

export interface Block {
  id: string;
  x: number;
  y: number;
  type: TetrominoType;
  color: string;
}

export interface Tetromino {
  type: TetrominoType;
  x: number;
  y: number;
  rotation: number;
  blocks: Block[];
}

export interface Player {
  id: string;
  name: string;
  score: number;
  health: number;
  currentTetromino: Tetromino | null;
  nextTetrominos: Tetromino[];
  heldTetromino: Tetromino | null;
  spells: SpellType[];
  towerBlocks: Block[];
}

export interface GameState {
  gameMode: GameMode;
  players: Record<string, Player>;
  score: number;
  level: number;
  linesCleared: number;
  timer: number;
  isGameOver: boolean;
}

export interface GameSettings {
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  speed: number;
  gravity: number;
  musicVolume: number;
  soundVolume: number;
  controls: {
    moveLeft: string;
    moveRight: string;
    rotate: string;
    drop: string;
    hold: string;
  };
} 