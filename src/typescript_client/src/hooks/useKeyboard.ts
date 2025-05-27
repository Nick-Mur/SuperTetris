import { useEffect, useCallback } from 'react';
import { GameSettings } from '../types/game';

interface UseKeyboardProps {
  settings: GameSettings;
  onMove: (direction: string) => void;
  onRotate: () => void;
  onDrop: () => void;
  onHold: () => void;
  isPaused: boolean;
}

export const useKeyboard = ({
  settings,
  onMove,
  onRotate,
  onDrop,
  onHold,
  isPaused
}: UseKeyboardProps) => {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (isPaused) return;

    const key = e.key.toLowerCase();

    switch (key) {
      case settings.controls.moveLeft.toLowerCase():
        onMove('left');
        break;
      case settings.controls.moveRight.toLowerCase():
        onMove('right');
        break;
      case settings.controls.rotate.toLowerCase():
        onRotate();
        break;
      case settings.controls.drop.toLowerCase():
        onDrop();
        break;
      case settings.controls.hold.toLowerCase():
        onHold();
        break;
    }
  }, [settings, onMove, onRotate, onDrop, onHold, isPaused]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}; 