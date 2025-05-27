import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { GameSettings } from '../components/GameSettings';
import { GameSettings as GameSettingsType } from '../types/game';

describe('GameSettings Component', () => {
  const mockSettings: GameSettingsType = {
    difficulty: 'MEDIUM',
    speed: 1.0,
    gravity: 1,
    musicVolume: 0.5,
    soundVolume: 0.5,
    controls: {
      moveLeft: 'ArrowLeft',
      moveRight: 'ArrowRight',
      rotate: 'ArrowUp',
      drop: 'ArrowDown',
      hold: 'c',
    },
  };

  const mockOnSave = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders game settings controls', () => {
    render(
      <GameSettings
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Game Settings')).toBeInTheDocument();
  });

  it('calls onSave with updated settings when save button is clicked', () => {
    render(
      <GameSettings
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );

    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);

    expect(mockOnSave).toHaveBeenCalledWith(expect.any(Object));
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(
      <GameSettings
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });
}); 