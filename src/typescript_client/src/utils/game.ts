import { Tetromino, TetrominoType, Block } from '../types/game';
import { TETROMINO_SHAPES, TETROMINO_COLORS } from '../constants/game';

export const createTetromino = (type: TetrominoType, x: number, y: number): Tetromino => {
  const shape = TETROMINO_SHAPES[type];
  const blocks: Block[] = shape.map(([dx, dy], index) => ({
    id: `${type}-${index}`,
    x: x + dx,
    y: y + dy,
    type,
    color: TETROMINO_COLORS[type]
  }));

  return {
    type,
    x,
    y,
    rotation: 0,
    blocks
  };
};

export const rotateTetromino = (tetromino: Tetromino): Tetromino => {
  const newRotation = (tetromino.rotation + 90) % 360;
  const blocks = tetromino.blocks.map(block => {
    const dx = block.x - tetromino.x;
    const dy = block.y - tetromino.y;
    const newX = tetromino.x - dy;
    const newY = tetromino.y + dx;
    return {
      ...block,
      x: newX,
      y: newY
    };
  });

  return {
    ...tetromino,
    rotation: newRotation,
    blocks
  };
};

export const moveTetromino = (tetromino: Tetromino, dx: number, dy: number): Tetromino => {
  const blocks = tetromino.blocks.map(block => ({
    ...block,
    x: block.x + dx,
    y: block.y + dy
  }));

  return {
    ...tetromino,
    x: tetromino.x + dx,
    y: tetromino.y + dy,
    blocks
  };
};

export const checkCollision = (
  tetromino: Tetromino,
  board: Block[],
  boardWidth: number,
  boardHeight: number
): boolean => {
  return tetromino.blocks.some(block => {
    // Проверка границ поля
    if (
      block.x < 0 ||
      block.x >= boardWidth ||
      block.y < 0 ||
      block.y >= boardHeight
    ) {
      return true;
    }

    // Проверка столкновения с другими блоками
    return board.some(
      boardBlock =>
        boardBlock.x === block.x && boardBlock.y === block.y
    );
  });
};

export const clearLines = (board: Block[], boardHeight: number): { newBoard: Block[], linesCleared: number } => {
  const lines: Block[][] = Array.from({ length: boardHeight }, () => []);
  
  // Распределяем блоки по линиям
  board.forEach(block => {
    if (block.y >= 0 && block.y < boardHeight) {
      lines[block.y].push(block);
    }
  });

  // Находим заполненные линии
  const filledLines = lines
    .map((line, y) => ({ line, y }))
    .filter(({ line }) => line.length === 10);

  if (filledLines.length === 0) {
    return { newBoard: board, linesCleared: 0 };
  }

  // Удаляем заполненные линии и сдвигаем блоки вниз
  const newBoard = board.filter(block => 
    !filledLines.some(({ y }) => block.y === y)
  ).map(block => {
    const linesAbove = filledLines.filter(({ y }) => y < block.y).length;
    return {
      ...block,
      y: block.y - linesAbove
    };
  });

  return {
    newBoard,
    linesCleared: filledLines.length
  };
}; 