import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import Game from '../Game';
import { GameMode } from '../types/game';

describe('Game Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders game menu initially', () => {
    render(<Game />);
    expect(screen.getByText('Tetris with Tricky Towers')).toBeInTheDocument();
    expect(screen.getByText('Race Mode')).toBeInTheDocument();
    expect(screen.getByText('Survival Mode')).toBeInTheDocument();
    expect(screen.getByText('Puzzle Mode')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('starts game when clicking on game mode', () => {
    render(<Game />);
    fireEvent.click(screen.getByText('Race Mode'));
    expect(screen.getByText('Game Paused')).toBeInTheDocument();
  });

  it('opens settings when clicking on settings button', () => {
    render(<Game />);
    fireEvent.click(screen.getByText('Settings'));
    expect(screen.getByText('Game Settings')).toBeInTheDocument();
  });

  it('pauses game when pressing Escape', () => {
    render(<Game />);
    fireEvent.click(screen.getByText('Race Mode'));
    act(() => {
      fireEvent.keyDown(document, { key: 'Escape' });
    });
    expect(screen.getByText('Game Paused')).toBeInTheDocument();
  });

  it('resumes game when pressing Escape while paused', () => {
    render(<Game />);
    fireEvent.click(screen.getByText('Race Mode'));
    act(() => {
      fireEvent.keyDown(document, { key: 'Escape' });
    });
    act(() => {
      fireEvent.keyDown(document, { key: 'Escape' });
    });
    expect(screen.queryByText('Game Paused')).not.toBeInTheDocument();
  });

  it('shows game over screen when game ends', () => {
    render(<Game />);
    fireEvent.click(screen.getByText('Race Mode'));
    // TODO: Добавить логику для завершения игры
    expect(screen.getByText('Game Over')).toBeInTheDocument();
  });

  it('returns to main menu when clicking main menu button', () => {
    render(<Game />);
    fireEvent.click(screen.getByText('Race Mode'));
    fireEvent.click(screen.getByText('Main Menu'));
    expect(screen.getByText('Tetris with Tricky Towers')).toBeInTheDocument();
  });

  it('renders GameMenu when gameMode is null', () => {
    // TODO: Добавить проверки на наличие GameMenu
  });

  it('renders GameOver when isGameOver is true', () => {
    // TODO: Добавить моки и проверки для состояния GameOver
  });

  it('renders GamePause when isPaused is true', () => {
    // TODO: Добавить моки и проверки для состояния GamePause
  });

  it('renders GameBoard when gameState is available', () => {
    // TODO: Добавить моки и проверки для состояния игры
  });

  it('handles Escape key to pause/resume', () => {
    // TODO: Добавить моки и проверки для обработки клавиши Escape
  });

  // TODO: Добавить тесты для других взаимодействий и состояний
}); 