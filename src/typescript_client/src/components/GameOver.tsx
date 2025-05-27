import React from 'react';
import { GameMode } from '../types/game';

interface GameOverProps {
  score: number;
  gameMode: GameMode;
  onRestart: () => void;
  onMainMenu: () => void;
}

export const GameOver: React.FC<GameOverProps> = ({
  score,
  gameMode,
  onRestart,
  onMainMenu
}) => {
  return (
    <div className="game-over">
      <h2>Game Over</h2>
      <div className="score-display">
        <p>Final Score: {score}</p>
        <p>Game Mode: {gameMode}</p>
      </div>
      <div className="button-group">
        <button onClick={onRestart}>Play Again</button>
        <button onClick={onMainMenu}>Main Menu</button>
      </div>
    </div>
  );
}; 