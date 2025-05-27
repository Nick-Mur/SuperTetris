import React from 'react';
import { render } from '@testing-library/react';
import { BlockDisplay } from '../components/BlockDisplay';
import { Block, TetrominoType } from '../types/game';

describe('BlockDisplay Component', () => {
  const mockBlock: Block = {
    id: 'mock-block-1',
    type: TetrominoType.I,
    x: 0,
    y: 0,
    color: '#00f0f0',
  };

  it('renders block with correct position and size', () => {
    const blockSize = 30;
    render(<BlockDisplay block={mockBlock} blockSize={blockSize} />);

    const blockElement = document.querySelector('.block');
    expect(blockElement).toHaveStyle({
      width: `${blockSize}px`,
      height: `${blockSize}px`,
      left: `${mockBlock.x * blockSize}px`,
      top: `${mockBlock.y * blockSize}px`,
    });
  });

  it('applies correct color class based on block type', () => {
    const { rerender } = render(
      <BlockDisplay block={mockBlock} blockSize={30} />
    );

    expect(document.querySelector('.block')).toHaveClass('i-block');

    const jBlock: Block = {
      id: 'mock-block-j',
      type: TetrominoType.J,
      x: 0,
      y: 0,
      color: '#0000ff',
    };

    rerender(<BlockDisplay block={jBlock} blockSize={30} />);
    expect(document.querySelector('.block')).toHaveClass('j-block');

    const lBlock: Block = {
      id: 'mock-block-l',
      type: TetrominoType.L,
      x: 0,
      y: 0,
      color: '#ff7f00',
    };

    rerender(<BlockDisplay block={lBlock} blockSize={30} />);
    expect(document.querySelector('.block')).toHaveClass('l-block');

    const oBlock: Block = {
      id: 'mock-block-o',
      type: TetrominoType.O,
      x: 0,
      y: 0,
      color: '#ffff00',
    };

    rerender(<BlockDisplay block={oBlock} blockSize={30} />);
    expect(document.querySelector('.block')).toHaveClass('o-block');

    const sBlock: Block = {
      id: 'mock-block-s',
      type: TetrominoType.S,
      x: 0,
      y: 0,
      color: '#00ff00',
    };

    rerender(<BlockDisplay block={sBlock} blockSize={30} />);
    expect(document.querySelector('.block')).toHaveClass('s-block');

    const tBlock: Block = {
      id: 'mock-block-t',
      type: TetrominoType.T,
      x: 0,
      y: 0,
      color: '#800080',
    };

    rerender(<BlockDisplay block={tBlock} blockSize={30} />);
    expect(document.querySelector('.block')).toHaveClass('t-block');

    const zBlock: Block = {
      id: 'mock-block-z',
      type: TetrominoType.Z,
      x: 0,
      y: 0,
      color: '#ff0000',
    };

    rerender(<BlockDisplay block={zBlock} blockSize={30} />);
    expect(document.querySelector('.block')).toHaveClass('z-block');
  });

  it('updates position when block position changes', () => {
    const { rerender } = render(
      <BlockDisplay block={mockBlock} blockSize={30} />
    );

    const newBlock: Block = {
      ...mockBlock,
      x: 5,
      y: 10,
    };

    rerender(<BlockDisplay block={newBlock} blockSize={30} />);

    const blockElement = document.querySelector('.block');
    expect(blockElement).toHaveStyle({
      left: `${newBlock.x * 30}px`,
      top: `${newBlock.y * 30}px`,
    });
  });

  it('updates size when blockSize prop changes', () => {
    const { rerender } = render(
      <BlockDisplay block={mockBlock} blockSize={30} />
    );

    const newSize = 40;
    rerender(<BlockDisplay block={mockBlock} blockSize={newSize} />);

    const blockElement = document.querySelector('.block');
    expect(blockElement).toHaveStyle({
      width: `${newSize}px`,
      height: `${newSize}px`,
      left: `${mockBlock.x * newSize}px`,
      top: `${mockBlock.y * newSize}px`,
    });
  });
}); 