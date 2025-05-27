import React from 'react';
import { Rect } from 'react-konva';
import { Block } from '../types/game';

interface BlockDisplayProps {
  block: Block;
  blockSize: number;
}

export const BlockDisplay: React.FC<BlockDisplayProps> = ({ block, blockSize }) => {
  return (
    <Rect
      x={block.x * blockSize}
      y={block.y * blockSize}
      width={blockSize}
      height={blockSize}
      fill={block.color}
      stroke="#000"
      strokeWidth={1}
    />
  );
}; 