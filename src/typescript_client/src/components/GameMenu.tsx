import React from 'react';
import { GameMode } from '../types/game';

interface GameMenuProps {
  onStartGame: (mode: GameMode) => void;
  onSettings: () => void;
}

export const GameMenu: React.FC<GameMenuProps> = ({ onStartGame, onSettings }) => {
  return (
    <div className="game-menu">
      <h1>Tetris</h1>
      <div className="menu-buttons">
        <button onClick={() => onStartGame(GameMode.RACE)}>Race Mode</button>
        <button onClick={() => onStartGame(GameMode.SURVIVAL)}>Survival Mode</button>
        <button onClick={() => onStartGame(GameMode.PUZZLE)}>Puzzle Mode</button>
        <button onClick={onSettings}>Settings</button>
      </div>
    </div>
  );
}; 