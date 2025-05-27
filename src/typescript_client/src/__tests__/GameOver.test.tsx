import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { GameOver } from '../components/GameOver';

describe('GameOver Component', () => {
  const mockOnRestart = jest.fn();
  const mockOnMainMenu = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders game over message and buttons', () => {
    render(
      <GameOver
        winner="Player 1"
        onRestart={mockOnRestart}
        onMainMenu={mockOnMainMenu}
      />
    );

    expect(screen.getByText('Game Over')).toBeInTheDocument();
    expect(screen.getByText('Winner: Player 1')).toBeInTheDocument();
    expect(screen.getByText('Restart')).toBeInTheDocument();
    expect(screen.getByText('Main Menu')).toBeInTheDocument();
  });

  it('calls onRestart when restart button is clicked', () => {
    render(
      <GameOver
        winner="Player 1"
        onRestart={mockOnRestart}
        onMainMenu={mockOnMainMenu}
      />
    );

    const restartButton = screen.getByText('Restart');
    fireEvent.click(restartButton);

    expect(mockOnRestart).toHaveBeenCalled();
  });

  it('calls onMainMenu when main menu button is clicked', () => {
    render(
      <GameOver
        winner="Player 1"
        onRestart={mockOnRestart}
        onMainMenu={mockOnMainMenu}
      />
    );

    const mainMenuButton = screen.getByText('Main Menu');
    fireEvent.click(mainMenuButton);

    expect(mockOnMainMenu).toHaveBeenCalled();
  });

  it('shows correct winner name', () => {
    render(
      <GameOver
        winner="Player 2"
        onRestart={mockOnRestart}
        onMainMenu={mockOnMainMenu}
      />
    );

    expect(screen.getByText('Winner: Player 2')).toBeInTheDocument();
  });

  it('applies correct styles to buttons', () => {
    render(
      <GameOver
        winner="Player 1"
        onRestart={mockOnRestart}
        onMainMenu={mockOnMainMenu}
      />
    );

    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveClass('game-over-button');
    });
  });
}); 