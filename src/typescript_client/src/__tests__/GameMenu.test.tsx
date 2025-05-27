import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { GameMenu } from '../components/GameMenu';
import { GameMode } from '../types/game';

describe('GameMenu Component', () => {
  const mockOnStartGame = jest.fn();
  const mockOnSettings = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all game modes and settings button', () => {
    render(
      <GameMenu onStartGame={mockOnStartGame} onSettings={mockOnSettings} />
    );

    expect(screen.getByText('Tetris with Tricky Towers')).toBeInTheDocument();
    expect(screen.getByText('Race Mode')).toBeInTheDocument();
    expect(screen.getByText('Survival Mode')).toBeInTheDocument();
    expect(screen.getByText('Puzzle Mode')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('calls onStartGame with correct mode when clicking game mode buttons', () => {
    render(
      <GameMenu onStartGame={mockOnStartGame} onSettings={mockOnSettings} />
    );

    fireEvent.click(screen.getByText('Race Mode'));
    expect(mockOnStartGame).toHaveBeenCalledWith(GameMode.RACE);

    fireEvent.click(screen.getByText('Survival Mode'));
    expect(mockOnStartGame).toHaveBeenCalledWith(GameMode.SURVIVAL);

    fireEvent.click(screen.getByText('Puzzle Mode'));
    expect(mockOnStartGame).toHaveBeenCalledWith(GameMode.PUZZLE);
  });

  it('calls onSettings when clicking settings button', () => {
    render(
      <GameMenu onStartGame={mockOnStartGame} onSettings={mockOnSettings} />
    );

    fireEvent.click(screen.getByText('Settings'));
    expect(mockOnSettings).toHaveBeenCalled();
  });

  it('applies correct styles to buttons', () => {
    render(
      <GameMenu onStartGame={mockOnStartGame} onSettings={mockOnSettings} />
    );

    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveClass('game-menu-button');
    });
  });
}); 