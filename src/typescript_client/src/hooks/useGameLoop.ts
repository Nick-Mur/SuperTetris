import { useEffect, useRef, useCallback } from 'react';
import { GameState } from '../types/game';

interface UseGameLoopProps {
  gameState: GameState | null;
  onUpdate: (deltaTime: number) => void;
  isPaused: boolean;
}

export const useGameLoop = ({ gameState, onUpdate, isPaused }: UseGameLoopProps) => {
  const lastTimeRef = useRef<number>(0);
  const animationFrameRef = useRef<number>();

  const gameLoop = useCallback((currentTime: number) => {
    if (!gameState || isPaused) {
      animationFrameRef.current = requestAnimationFrame(gameLoop);
      return;
    }

    if (lastTimeRef.current === 0) {
      lastTimeRef.current = currentTime;
      animationFrameRef.current = requestAnimationFrame(gameLoop);
      return;
    }

    const deltaTime = (currentTime - lastTimeRef.current) / 1000;
    lastTimeRef.current = currentTime;

    onUpdate(deltaTime);

    animationFrameRef.current = requestAnimationFrame(gameLoop);
  }, [gameState, isPaused, onUpdate]);

  useEffect(() => {
    animationFrameRef.current = requestAnimationFrame(gameLoop);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [gameLoop]);
}; 