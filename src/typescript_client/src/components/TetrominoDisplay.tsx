import React from 'react';
import { Group, Rect } from 'react-konva';
import { Tetromino } from '../types/game';
import { TETROMINO_COLORS, TETROMINO_SHAPES } from '../constants/game';

interface TetrominoDisplayProps {
  tetromino: Tetromino;
  blockSize: number;
  x?: number;
  y?: number;
  scale?: number;
}

export const TetrominoDisplay: React.FC<TetrominoDisplayProps> = ({
  tetromino,
  blockSize,
  x = 0,
  y = 0,
  scale = 1
}) => {
  const shape = TETROMINO_SHAPES[tetromino.type];
  const color = TETROMINO_COLORS[tetromino.type];
  
  return (
    <Group x={x} y={y} scaleX={scale} scaleY={scale}>
      {shape.map((pos, index) => (
        <Rect
          key={index}
          x={pos[0] * blockSize}
          y={pos[1] * blockSize}
          width={blockSize}
          height={blockSize}
          fill={color}
          stroke="#000"
          strokeWidth={1}
        />
      ))}
    </Group>
  );
}; 