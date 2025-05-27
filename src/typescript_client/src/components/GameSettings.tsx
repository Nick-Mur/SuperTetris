import React, { useState } from 'react';
import { GameSettings as GameSettingsType } from '../types/game';
import { DEFAULT_GAME_SETTINGS } from '../constants/game';

interface GameSettingsProps {
  onSave: (settings: GameSettingsType) => void;
  onCancel: () => void;
}

export const GameSettings: React.FC<GameSettingsProps> = ({ onSave, onCancel }) => {
  const [settings, setSettings] = useState<GameSettingsType>(DEFAULT_GAME_SETTINGS);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name.startsWith('controls.')) {
      const controlName = name.split('.')[1];
      setSettings(prev => ({
        ...prev,
        controls: {
          ...prev.controls,
          [controlName]: value
        }
      }));
    } else {
      setSettings(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  return (
    <div className="game-settings">
      <h2>Settings</h2>
      <form onSubmit={(e) => {
        e.preventDefault();
        onSave(settings);
      }}>
        <div className="setting-group">
          <label>
            Difficulty:
            <select name="difficulty" value={settings.difficulty} onChange={handleChange}>
              <option value="EASY">Easy</option>
              <option value="MEDIUM">Medium</option>
              <option value="HARD">Hard</option>
            </select>
          </label>
        </div>
        
        <div className="setting-group">
          <label>
            Game Speed:
            <input
              type="range"
              name="speed"
              min="0.5"
              max="2"
              step="0.1"
              value={settings.speed}
              onChange={handleChange}
            />
            {settings.speed}x
          </label>
        </div>
        
        <div className="setting-group">
          <label>
            Gravity:
            <input
              type="range"
              name="gravity"
              min="0.5"
              max="2"
              step="0.1"
              value={settings.gravity}
              onChange={handleChange}
            />
            {settings.gravity}x
          </label>
        </div>
        
        <div className="setting-group">
          <label>
            Music Volume:
            <input
              type="range"
              name="musicVolume"
              min="0"
              max="1"
              step="0.1"
              value={settings.musicVolume}
              onChange={handleChange}
            />
            {Math.round(settings.musicVolume * 100)}%
          </label>
        </div>
        
        <div className="setting-group">
          <label>
            Sound Volume:
            <input
              type="range"
              name="soundVolume"
              min="0"
              max="1"
              step="0.1"
              value={settings.soundVolume}
              onChange={handleChange}
            />
            {Math.round(settings.soundVolume * 100)}%
          </label>
        </div>
        
        <div className="setting-group">
          <h3>Controls</h3>
          <label>
            Move Left:
            <input
              type="text"
              name="controls.moveLeft"
              value={settings.controls.moveLeft}
              onChange={handleChange}
            />
          </label>
          <label>
            Move Right:
            <input
              type="text"
              name="controls.moveRight"
              value={settings.controls.moveRight}
              onChange={handleChange}
            />
          </label>
          <label>
            Rotate:
            <input
              type="text"
              name="controls.rotate"
              value={settings.controls.rotate}
              onChange={handleChange}
            />
          </label>
          <label>
            Drop:
            <input
              type="text"
              name="controls.drop"
              value={settings.controls.drop}
              onChange={handleChange}
            />
          </label>
          <label>
            Hold:
            <input
              type="text"
              name="controls.hold"
              value={settings.controls.hold}
              onChange={handleChange}
            />
          </label>
        </div>
        
        <div className="button-group">
          <button type="submit">Save</button>
          <button type="button" onClick={onCancel}>Cancel</button>
        </div>
      </form>
    </div>
  );
}; 