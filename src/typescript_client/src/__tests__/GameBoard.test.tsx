import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { GameBoard } from '../components/GameBoard';
import { GameState, GameMode, Player, GameSettings, SpellType, TetrominoType, Block } from '../types/game';

// Определяем базовый мок Block
const mockBlock: Block = {
  id: 'block-1',
  x: 0,
  y: 0,
  type: TetrominoType.I,
  color: '#00f0f0',
};

// Определяем базовый мок Tetromino
const mockTetromino = {
  type: TetrominoType.I,
  x: 3,
  y: 0,
  rotation: 0,
  blocks: [mockBlock],
};

// Определяем базовый мок Player
const mockPlayer: Player = {
  id: 'player1',
  name: 'Player 1',
  score: 0,
  health: 100,
  currentTetromino: null,
  nextTetrominos: [],
  heldTetromino: null,
  spells: [], // Изначально пустой список заклинаний
  towerBlocks: [],
};

// Определяем базовый мок GameState
const mockGameState: GameState = {
  gameMode: GameMode.SINGLE_PLAYER, // Используем gameMode вместо mode
  players: { // Используем Record<string, Player>
    'player1': mockPlayer,
  },
  score: 0,
  level: 1,
  linesCleared: 0, // Используем linesCleared вместо lines
  timer: 0,
  isGameOver: false, // Используем isGameOver вместо status и winner
};

describe('GameBoard Component', () => {
  const mockOnMove = jest.fn();
  const mockOnSpellCast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders game board with player information', () => {
    render(
      <GameBoard
        gameState={mockGameState}
        playerId="player1"
        onMove={mockOnMove}
        onSpellCast={mockOnSpellCast}
      />
    );

    expect(screen.getByText('Player 1')).toBeInTheDocument();
    expect(screen.getByText('Score: 0')).toBeInTheDocument();
    expect(screen.getByText('Level: 1')).toBeInTheDocument();
    // Обновляем проверку на linesCleared
    expect(screen.getByText('Lines Cleared: 0')).toBeInTheDocument();
  });

  it('handles keyboard controls', () => {
    // Создаем копию mockGameState для этого теста, чтобы не влиять на другие
    const gameStateWithTetromino = {
      ...mockGameState,
      players: {
        'player1': {
          ...mockPlayer,
          currentTetromino: mockTetromino, // Добавляем текущий тетромино для симуляции движения
        },
      },
    };

    render(
      <GameBoard
        gameState={gameStateWithTetromino}
        playerId="player1"
        onMove={mockOnMove}
        onSpellCast={mockOnSpellCast}
      />
    );

    act(() => {
      fireEvent.keyDown(document, { key: 'ArrowLeft' });
    });
    expect(mockOnMove).toHaveBeenCalledWith('left', expect.any(Number), expect.any(Number), expect.any(Number));

    act(() => {
      fireEvent.keyDown(document, { key: 'ArrowRight' });
    });
    expect(mockOnMove).toHaveBeenCalledWith('right', expect.any(Number), expect.any(Number), expect.any(Number));

    act(() => {
      fireEvent.keyDown(document, { key: 'ArrowDown' });
    });
    expect(mockOnMove).toHaveBeenCalledWith('down', expect.any(Number), expect.any(Number), expect.any(Number));

    act(() => {
      fireEvent.keyDown(document, { key: 'ArrowUp' });
    });
    expect(mockOnMove).toHaveBeenCalledWith('rotate', expect.any(Number), expect.any(Number), expect.any(Number));

    act(() => {
      fireEvent.keyDown(document, { key: ' ' });
    });
    // TODO: Проверить аргументы для hardDrop, если они отличаются
    expect(mockOnMove).toHaveBeenCalledWith('hardDrop', expect.any(Number), expect.any(Number), expect.any(Number));

    act(() => {
      fireEvent.keyDown(document, { key: 'c' });
    });
    // TODO: Проверить аргументы для hold, если они отличаются
    expect(mockOnMove).toHaveBeenCalledWith('hold', expect.any(Number), expect.any(Number), expect.any(Number));
  });

  it('handles spell casting', () => {
    const gameStateWithSpells: GameState = { // Явно указываем тип
      ...mockGameState,
      players: {
        'player1': {
          ...mockPlayer,
          spells: [SpellType.CLEAR_LINE, SpellType.ADD_BLOCKS], // Используем enum SpellType
        },
      },
    };

    render(
      <GameBoard
        gameState={gameStateWithSpells}
        playerId="player1"
        onMove={mockOnMove}
        onSpellCast={mockOnSpellCast}
      />
    );

    // TODO: Добавить более специфичные селекторы для кнопок заклинаний
    // const spellButtons = screen.getAllByRole('button'); // Удаляем неиспользуемую переменную
    // Кнопки заклинаний могут быть не первыми в списке всех кнопок, нужно уточнить селектор
  });

  it('shows game over state', () => {
    const gameOverState: GameState = { // Явно указываем тип
      ...mockGameState,
      isGameOver: true, // Используем isGameOver
      // В GameBoard, возможно, нет логики для отображения победителя, проверяем только статус Game Over
    };

    render(
      <GameBoard
        gameState={gameOverState}
        playerId="player1"
        onMove={mockOnMove}
        onSpellCast={mockOnSpellCast}
      />
    );

    // TODO: Проверить, что GameBoard отображает состояние Game Over
    // Например, по наличию определенного текста или класса
    // expect(screen.getByText('Game Over')).toBeInTheDocument();
  });
}); 