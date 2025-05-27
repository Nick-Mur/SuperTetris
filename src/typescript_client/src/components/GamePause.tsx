import React from 'react';

interface GamePauseProps {
  onResume: () => void;
  onSettings: () => void;
  onMainMenu: () => void;
}

export const GamePause: React.FC<GamePauseProps> = ({
  onResume,
  onSettings,
  onMainMenu
}) => {
  return (
    <div className="game-pause">
      <h2>Game Paused</h2>
      <div className="button-group">
        <button onClick={onResume}>Resume</button>
        <button onClick={onSettings}>Settings</button>
        <button onClick={onMainMenu}>Main Menu</button>
      </div>
    </div>
  );
}; 