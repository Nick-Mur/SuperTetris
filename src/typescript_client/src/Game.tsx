import React, { useEffect, useState, useCallback } from 'react';
import { GameBoard } from './components/GameBoard';
import { GameMenu } from './components/GameMenu';
import { GameSettings } from './components/GameSettings';
import { GameOver } from './components/GameOver';
import { GamePause } from './components/GamePause';
import { GameMode, GameState, GameSettings as GameSettingsType } from './types/game';
import { DEFAULT_GAME_SETTINGS } from './constants/game';
import './styles/index.css';
import './styles/components.css';

// Стили
import './GameUI.css';

// Основной компонент игры
const Game: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [gameMode, setGameMode] = useState<GameMode | null>(null);
  const [settings, setSettings] = useState<GameSettingsType>(DEFAULT_GAME_SETTINGS);
  const [isPaused, setIsPaused] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);
  // TODO: Реализовать WebSocket
  // const [socket, setSocket] = useState<WebSocket | null>(null);

  const handleStartGame = useCallback((mode: GameMode) => {
    setGameMode(mode);
    setIsPaused(false);
    setIsSettingsOpen(false);
    setIsGameOver(false);
    // TODO: Инициализация игрового состояния
  }, []);

  const handlePause = useCallback(() => {
    setIsPaused(true);
  }, []);

  const handleResume = useCallback(() => {
    setIsPaused(false);
  }, []);

  const handleSettings = useCallback(() => {
    setIsSettingsOpen(true);
  }, []);

  const handleSettingsSave = useCallback((newSettings: GameSettingsType) => {
    setSettings(newSettings);
    setIsSettingsOpen(false);
  }, []);

  const handleSettingsCancel = useCallback(() => {
    setIsSettingsOpen(false);
  }, []);

  const handleGameOver = useCallback(() => {
    // TODO: Реализовать логику завершения игры
    setIsGameOver(true);
  }, []);

  const handleRestart = useCallback(() => {
    // TODO: Реализовать логику перезапуска игры
    if (gameMode) {
      handleStartGame(gameMode);
    }
  }, [gameMode, handleStartGame]);

  const handleMainMenu = useCallback(() => {
    // TODO: Реализовать логику возврата в главное меню
    setGameState(null);
    setGameMode(null);
    setIsPaused(false);
    setIsSettingsOpen(false);
    setIsGameOver(false);
  }, []);
  
  const handleMove = useCallback((/* direction: string */) => {
    // TODO: Обработка движения игрока
    // console.log('Move:', direction);
  }, []); // Зависимости могут быть пустыми, если direction не используется

  const handleSpellCast = useCallback((/* spellType: string */) => {
    // TODO: Обработка заклинаний
    // console.log('Spell Cast:', spellType);
  }, []); // Зависимости могут быть пустыми, если spellType не используется

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isPaused) {
          handleResume();
        } else {
          handlePause();
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isPaused, handlePause, handleResume]);

  // Эффект для инициализации WebSocket
  useEffect(() => {
    // TODO: Инициализация WebSocket и обработка сообщений
    // Пример подключения (нужно будет адаптировать под ваш API)
    // const ws = new WebSocket('ws://localhost:8080/ws/game/' + gameId);
    // setSocket(ws);

    // return () => {
    //   ws.close();
    // };
  }, [/* gameId, setSocket */]); // Зависимости для WebSocket

  // Рендеринг игры в зависимости от состояния
  if (!gameMode) {
  return (
    <div className="game-container">
        <GameMenu onStartGame={handleStartGame} onSettings={handleSettings} />
        {isSettingsOpen && (
          <GameSettings onSave={handleSettingsSave} onCancel={handleSettingsCancel} />
        )}
    </div>
  );
  }

  if (isGameOver) {
  return (
      <div className="game-container">
        <GameOver score={gameState?.score || 0} gameMode={gameMode} onRestart={() => handleStartGame(gameMode)} onMainMenu={() => setGameMode(null)} />
    </div>
  );
  }

  if (isPaused) {
  return (
      <div className="game-container">
        <GamePause onResume={handleResume} onSettings={handleSettings} onMainMenu={() => setGameMode(null)} />
        {isSettingsOpen && (
          <GameSettings onSave={handleSettingsSave} onCancel={handleSettingsCancel} />
        )}
    </div>
  );
  }

    if (gameState) {
    // TODO: Передать правильный playerId и реализовать логику onMove/onSpellCast
        return (
      <div className="game-container">
        {/* Передача правильных пропсов в GameBoard */}
            <GameBoard
              gameState={gameState}
          playerId="player-1" // Замените на реальный playerId
          onMove={(/* moveType, x, y, rotation */) => { /* TODO: Обработка движения */ }}
          onSpellCast={(/* spell, targetId */) => { /* TODO: Обработка заклинания */ }}
        />
        {/* TODO: Отображение другой информации: счет, уровень, заклинания и т.д. */}
    </div>
  );
  }

  return <div>Загрузка игры...</div>; // Или другой индикатор загрузки
};

export default Game;
