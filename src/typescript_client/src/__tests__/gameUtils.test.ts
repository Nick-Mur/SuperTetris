import {
  createTetromino,
  rotateTetromino,
  moveTetromino,
  checkCollision,
  clearLines
} from '../utils/game';
import { TetrominoType, Block } from '../types/game';

describe('Game Utils', () => {
  describe('createTetromino', () => {
    it('creates I tetromino', () => {
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      expect(tetromino.type).toBe(TetrominoType.I);
      expect(tetromino.blocks).toHaveLength(4);
      expect(tetromino.x).toBe(3);
      expect(tetromino.y).toBe(0);
    });

    it('creates O tetromino', () => {
      const tetromino = createTetromino(TetrominoType.O, 4, 0);
      expect(tetromino.type).toBe(TetrominoType.O);
      expect(tetromino.blocks).toHaveLength(4);
      expect(tetromino.x).toBe(4);
      expect(tetromino.y).toBe(0);
    });
  });

  describe('rotateTetromino', () => {
    it('rotates I tetromino', () => {
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      const rotated = rotateTetromino(tetromino);
      expect(rotated.blocks).not.toEqual(tetromino.blocks);
      expect(rotated.rotation).toBe(90);
    });

    it('rotates O tetromino (no change)', () => {
      const tetromino = createTetromino(TetrominoType.O, 4, 0);
      const rotated = rotateTetromino(tetromino);
      expect(rotated.blocks).toEqual(tetromino.blocks);
      expect(rotated.rotation).toBe(90);
    });
  });

  describe('moveTetromino', () => {
    it('moves tetromino left', () => {
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      const moved = moveTetromino(tetromino, -1, 0);
      expect(moved.x).toBe(2);
      expect(moved.y).toBe(0);
    });

    it('moves tetromino right', () => {
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      const moved = moveTetromino(tetromino, 1, 0);
      expect(moved.x).toBe(4);
      expect(moved.y).toBe(0);
    });

    it('moves tetromino down', () => {
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      const moved = moveTetromino(tetromino, 0, 1);
      expect(moved.x).toBe(3);
      expect(moved.y).toBe(1);
    });
  });

  describe('checkCollision', () => {
    const boardWidth = 10;
    const boardHeight = 20;
    const board: Block[] = [];

    it('detects collision with board boundaries', () => {
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      const movedLeft = moveTetromino(tetromino, -4, 0);
      const movedRight = moveTetromino(tetromino, 7, 0);
      const movedDown = moveTetromino(tetromino, 0, 17);

      expect(checkCollision(movedLeft, board, boardWidth, boardHeight)).toBe(true);
      expect(checkCollision(movedRight, board, boardWidth, boardHeight)).toBe(true);
      expect(checkCollision(movedDown, board, boardWidth, boardHeight)).toBe(true);
    });

    it('detects collision with other blocks', () => {
      const boardWithBlocks: Block[] = [
        { id: '1', x: 3, y: 1, type: TetrominoType.I, color: '#00f0f0' },
        { id: '2', x: 4, y: 1, type: TetrominoType.I, color: '#00f0f0' },
        { id: '3', x: 5, y: 1, type: TetrominoType.I, color: '#00f0f0' },
        { id: '4', x: 6, y: 1, type: TetrominoType.I, color: '#00f0f0' }
      ];
      const tetromino = createTetromino(TetrominoType.I, 3, 0);
      const movedDown = moveTetromino(tetromino, 0, 1);
      expect(checkCollision(movedDown, boardWithBlocks, boardWidth, boardHeight)).toBe(true);
    });
  });

  describe('clearLines', () => {
    it('clears completed lines', () => {
      const boardHeight = 20;
      const board: Block[] = Array.from({ length: 10 }, (_, x) => ({
        id: `block-${x}`,
        x,
        y: 5,
        type: TetrominoType.I,
        color: '#00f0f0'
      }));

      const { newBoard, linesCleared } = clearLines(board, boardHeight);
      expect(linesCleared).toBe(1);
      expect(newBoard.length).toBe(0);
    });

    it('shifts blocks down after clearing lines', () => {
      const boardHeight = 20;
      const board: Block[] = [
        // Completed line
        ...Array.from({ length: 10 }, (_, x) => ({
          id: `block-${x}`,
          x,
          y: 5,
          type: TetrominoType.I,
          color: '#00f0f0'
        })),
        // Block above
        {
          id: 'block-above',
          x: 5,
          y: 4,
          type: TetrominoType.I,
          color: '#00f0f0'
        }
      ];

      const { newBoard, linesCleared } = clearLines(board, boardHeight);
      expect(linesCleared).toBe(1);
      expect(newBoard.length).toBe(1);
      expect(newBoard[0].y).toBe(4);
    });
  });
}); 