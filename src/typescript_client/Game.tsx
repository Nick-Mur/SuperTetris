import React, { useEffect, useState, useRef } from 'react';
import { Stage, Layer, Rect, Text, Group } from 'react-konva';
import { useSpring, animated } from 'react-spring';
import { KonvaNodeComponent } from 'react-konva';

// Стили
import './GameUI.css';

// Типы тетромино
enum TetrominoType {
  I = 'I',
  J = 'J',
  L = 'L',
  O = 'O',
  S = 'S',
  T = 'T',
  Z = 'Z'
}

// Типы заклинаний
enum SpellType {
  // Светлая магия
  REINFORCE = 'REINFORCE',   // Укрепление блоков
  STABILIZE = 'STABILIZE',   // Стабилизация башни
  ENLARGE = 'ENLARGE',       // Увеличение блока
  SHRINK = 'SHRINK',         // Уменьшение блока
  LEVITATE = 'LEVITATE',     // Левитация блока
  
  // Тёмная магия
  EARTHQUAKE = 'EARTHQUAKE', // Землетрясение
  WIND = 'WIND',             // Ветер
  SLIPPERY = 'SLIPPERY',     // Скользкие блоки
  CONFUSION = 'CONFUSION',   // Путаница управления
  ACCELERATE = 'ACCELERATE'  // Ускорение падения
}

// Режимы игры
enum GameMode {
  RACE = 'RACE',
  SURVIVAL = 'SURVIVAL',
  PUZZLE = 'PUZZLE'
}

// Интерфейсы для типов данных
interface Block {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  color: string;
  density: number;
  friction: number;
  restitution: number;
  isStatic: boolean;
}

interface Tetromino {
  type: TetrominoType;
  x: number;
  y: number;
  rotation: number;
}

interface Player {
  id: number;
  name: string;
  towerBlocks: Block[];
  currentTetromino: Tetromino | null;
  nextTetrominos: Tetromino[];
  heldTetromino: Tetromino | null;
  spells: SpellType[];
  score: number;
  health: number;
}

interface GameState {
  players: { [key: string]: Player };
  gameMode: GameMode;
  currentTurn: number;
  gameStatus: string;
  timer: number;
}

// Конфигурация цветов для тетромино
const TETROMINO_COLORS = {
  [TetrominoType.I]: '#00FFFF', // Cyan
  [TetrominoType.J]: '#0000FF', // Blue
  [TetrominoType.L]: '#FF7F00', // Orange
  [TetrominoType.O]: '#FFFF00', // Yellow
  [TetrominoType.S]: '#00FF00', // Green
  [TetrominoType.T]: '#800080', // Purple
  [TetrominoType.Z]: '#FF0000'  // Red
};

// Конфигурация форм тетромино
const TETROMINO_SHAPES = {
  [TetrominoType.I]: [
    [0, 0], [1, 0], [2, 0], [3, 0]
  ],
  [TetrominoType.J]: [
    [0, 0], [0, 1], [1, 1], [2, 1]
  ],
  [TetrominoType.L]: [
    [2, 0], [0, 1], [1, 1], [2, 1]
  ],
  [TetrominoType.O]: [
    [0, 0], [1, 0], [0, 1], [1, 1]
  ],
  [TetrominoType.S]: [
    [1, 0], [2, 0], [0, 1], [1, 1]
  ],
  [TetrominoType.T]: [
    [1, 0], [0, 1], [1, 1], [2, 1]
  ],
  [TetrominoType.Z]: [
    [0, 0], [1, 0], [1, 1], [2, 1]
  ]
};

// Конфигурация иконок заклинаний
const SPELL_ICONS = {
  [SpellType.REINFORCE]: '🛡️',
  [SpellType.STABILIZE]: '⚓',
  [SpellType.ENLARGE]: '🔍',
  [SpellType.SHRINK]: '🔎',
  [SpellType.LEVITATE]: '🪄',
  [SpellType.EARTHQUAKE]: '🌋',
  [SpellType.WIND]: '🌪️',
  [SpellType.SLIPPERY]: '🧊',
  [SpellType.CONFUSION]: '😵',
  [SpellType.ACCELERATE]: '⏩'
};

// Компонент для отображения тетромино
const TetrominoDisplay: React.FC<{
  tetromino: Tetromino;
  blockSize: number;
  x?: number;
  y?: number;
  scale?: number;
}> = ({ tetromino, blockSize, x = 0, y = 0, scale = 1 }) => {
  const shape = TETROMINO_SHAPES[tetromino.type];
  const color = TETROMINO_COLORS[tetromino.type];
  
  return (
    <Group x={x} y={y} scaleX={scale} scaleY={scale}>
      {shape.map((pos, index) => (
        <Rect
          key={index}
          x={pos[0] * blockSize}
          y={pos[1] * blockSize}
          width={blockSize}
          height={blockSize}
          fill={color}
          stroke="#000"
          strokeWidth={1}
        />
      ))}
    </Group>
  );
};

// Компонент для отображения блока
const BlockDisplay: React.FC<{
  block: Block;
  blockSize: number;
}> = ({ block, blockSize }) => {
  return (
    <Rect
      x={block.x * blockSize}
      y={block.y * blockSize}
      width={block.width * blockSize}
      height={block.height * blockSize}
      fill={block.color}
      stroke="#000"
      strokeWidth={1}
      rotation={block.rotation}
    />
  );
};

// Компонент для отображения заклинания
const SpellDisplay: React.FC<{
  spell: SpellType;
  onClick: () => void;
  isActive: boolean;
}> = ({ spell, onClick, isActive }) => {
  return (
    <div 
      className={`spell-icon ${isActive ? 'active' : ''}`} 
      onClick={onClick}
      title={spell}
    >
      {SPELL_ICONS[spell]}
    </div>
  );
};

// Компонент для отображения игрового поля
const GameBoard: React.FC<{
  gameState: GameState;
  playerId: number;
  onMove: (moveType: string, x: number, y: number, rotation: number) => void;
  onSpellCast: (spell: SpellType, targetId: number) => void;
}> = ({ gameState, playerId, onMove, onSpellCast }) => {
  const [selectedSpell, setSelectedSpell] = useState<SpellType | null>(null);
  const [selectedTarget, setSelectedTarget] = useState<number | null>(null);
  const [blockSize, setBlockSize] = useState(30);
  const boardRef = useRef<HTMLDivElement>(null);
  
  // Получение текущего игрока
  const currentPlayer = gameState.players[playerId.toString()];
  
  // Обработка изменения размера окна
  useEffect(() => {
    const handleResize = () => {
      if (boardRef.current) {
        const width = boardRef.current.clientWidth;
        const height = boardRef.current.clientHeight;
        const newBlockSize = Math.min(width / 10, height / 20);
        setBlockSize(newBlockSize);
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  // Обработка нажатий клавиш
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!currentPlayer || !currentPlayer.currentTetromino) return;
      
      const { x, y, rotation } = currentPlayer.currentTetromino;
      
      switch (e.key) {
        case 'ArrowLeft':
          onMove('move_left', x - 1, y, rotation);
          break;
        case 'ArrowRight':
          onMove('move_right', x + 1, y, rotation);
          break;
        case 'ArrowDown':
          onMove('move_down', x, y + 1, rotation);
          break;
        case 'ArrowUp':
          onMove('rotate', x, y, (rotation + 90) % 360);
          break;
        case ' ':
          onMove('drop', x, y, rotation);
          break;
        case 'c':
        case 'C':
          onMove('hold', x, y, rotation);
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentPlayer, onMove]);
  
  // Обработка использования заклинания
  const handleSpellClick = (spell: SpellType) => {
    setSelectedSpell(spell);
  };
  
  // Обработка выбора цели заклинания
  const handleTargetClick = (targetId: number) => {
    if (selectedSpell) {
      onSpellCast(selectedSpell, targetId);
      setSelectedSpell(null);
      setSelectedTarget(null);
    } else {
      setSelectedTarget(targetId);
    }
  };
  
  // Если нет текущего игрока, показываем сообщение об ошибке
  if (!currentPlayer) {
    return <div className="error-message">Player not found</div>;
  }
  
  return (
    <div className="game-container">
      <div className="game-board" ref={boardRef}>
        <Stage width={blockSize * 10} height={blockSize * 20}>
          <Layer>
            {/* Сетка игрового поля */}
            {Array.from({ length: 10 }).map((_, x) => (
              <Rect
                key={`grid-x-${x}`}
                x={x * blockSize}
                y={0}
                width={1}
                height={blockSize * 20}
                fill="#333"
              />
            ))}
            {Array.from({ length: 20 }).map((_, y) => (
              <Rect
                key={`grid-y-${y}`}
                x={0}
                y={y * blockSize}
                width={blockSize * 10}
                height={1}
                fill="#333"
              />
            ))}
            
            {/* Блоки башни */}
            {currentPlayer.towerBlocks.map((block) => (
              <BlockDisplay
                key={`block-${block.id}`}
                block={block}
                blockSize={blockSize}
              />
            ))}
            
            {/* Текущее тетромино */}
            {currentPlayer.currentTetromino && (
              <TetrominoDisplay
                tetromino={currentPlayer.currentTetromino}
                blockSize={blockSize}
                x={currentPlayer.currentTetromino.x * blockSize}
                y={currentPlayer.currentTetromino.y * blockSize}
              />
            )}
          </Layer>
        </Stage>
      </div>
      
      <div className="game-sidebar">
        <div className="player-info">
          <h3>{currentPlayer.name}</h3>
          <div className="score">Score: {currentPlayer.score}</div>
          <div className="health">
            Health: {Array.from({ length: currentPlayer.health }).map((_, i) => (
              <span key={i} className="health-icon">❤️</span>
            ))}
          </div>
        </div>
        
        <div className="next-tetromino">
          <h4>Next</h4>
          {currentPlayer.nextTetrominos.length > 0 && (
            <TetrominoDisplay
              tetromino={currentPlayer.nextTetrominos[0]}
              blockSize={blockSize * 0.8}
              scale={0.8}
            />
          )}
        </div>
        
        <div className="held-tetromino">
          <h4>Hold</h4>
          {currentPlayer.heldTetromino && (
            <TetrominoDisplay
              tetromino={currentPlayer.heldTetromino}
              blockSize={blockSize * 0.8}
              scale={0.8}
            />
          )}
        </div>
        
        <div className="spells">
          <h4>Spells</h4>
          <div className="spell-list">
            {currentPlayer.spells.map((spell, index) => (
              <SpellDisplay
                key={`spell-${index}`}
                spell={spell}
                onClick={() => handleSpellClick(spell)}
                isActive={selectedSpell === spell}
              />
            ))}
          </div>
        </div>
        
        <div className="opponents">
          <h4>Opponents</h4>
          {Object.values(gameState.players)
            .filter(player => player.id !== playerId)
            .map(player => (
              <div 
                key={`opponent-${player.id}`} 
                className={`opponent ${selectedTarget === player.id ? 'selected' : ''}`}
                onClick={() => handleTargetClick(player.id)}
              >
                <div className="opponent-name">{player.name}</div>
                <div className="opponent-score">Score: {player.score}</div>
                <div className="opponent-health">
                  Health: {Array.from({ length: player.health }).map((_, i) => (
                    <span key={i} className="health-icon">❤️</span>
                  ))}
                </div>
              </div>
            ))}
        </div>
        
        <div className="game-controls">
          <button onClick={() => onMove('move_left', 0, 0, 0)}>←</button>
          <button onClick={() => onMove('move_down', 0, 0, 0)}>↓</button>
          <button onClick={() => onMove('move_right', 0, 0, 0)}>→</button>
          <button onClick={() => onMove('rotate', 0, 0, 0)}>↻</button>
          <button onClick={() => onMove('drop', 0, 0, 0)}>Drop</button>
          <button onClick={() => onMove('hold', 0, 0, 0)}>Hold</button>
        </div>
      </div>
    </div>
  );
};

// Компонент для отображения меню игры
const GameMenu: React.FC<{
  onStartGame: (mode: GameMode) => void;
  onSettings: () => void;
}> = ({ onStartGame, onSettings }) => {
  return (
    <div className="game-menu">
      <h1>Tetris with Tricky Towers</h1>
      <div className="menu-buttons">
        <button onClick={() => onStartGame(GameMode.RACE)}>Race Mode</button>
        <button onClick={() => onStartGame(GameMode.SURVIVAL)}>Survival Mode</button>
        <button onClick={() => onStartGame(GameMode.PUZZLE)}>Puzzle Mode</button>
        <button onClick={onSettings}>Settings</button>
      </div>
    </div>
  );
};

// Компонент для отображения настроек игры
const GameSettings: React.FC<{
  onSave: (settings: any) => void;
  onCancel: () => void;
}> = ({ onSave, onCancel }) => {
  const [settings, setSettings] = useState({
    playerName: 'Player 1',
    volume: 50,
    musicEnabled: true,
    soundEnabled: true,
    difficulty: 'medium'
  });
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const newValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;
    
    setSettings({
      ...settings,
      [name]: newValue
    });
  };
  
  return (
    <div className="game-settings">
      <h2>Settings</h2>
      <form onSubmit={(e) => { e.preventDefault(); onSave(settings); }}>
        <div className="form-group">
          <label htmlFor="playerName">Player Name</label>
          <input
            type="text"
            id="playerName"
            name="playerName"
            value={settings.playerName}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="volume">Volume</label>
          <input
            type="range"
            id="volume"
            name="volume"
            min="0"
            max="100"
            value={settings.volume}
            onChange={handleChange}
          />
          <span>{settings.volume}%</span>
        </div>
        
        <div className="form-group">
          <label htmlFor="musicEnabled">Music</label>
          <input
            type="checkbox"
            id="musicEnabled"
            name="musicEnabled"
            checked={settings.musicEnabled}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="soundEnabled">Sound Effects</label>
          <input
            type="checkbox"
            id="soundEnabled"
            name="soundEnabled"
            checked={settings.soundEnabled}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="difficulty">Difficulty</label>
          <select
            id="difficulty"
            name="difficulty"
            value={settings.difficulty}
            onChange={handleChange}
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
        
        <div className="form-buttons">
          <button type="submit">Save</button>
          <button type="button" onClick={onCancel}>Cancel</button>
        </div>
      </form>
    </div>
  );
};

// Компонент для отображения экрана окончания игры
const GameOver: React.FC<{
  gameState: GameState;
  playerId: number;
  onRestart: () => void;
  onMainMenu: () => void;
}> = ({ gameState, playerId, onRestart, onMainMenu }) => {
  // Определение победителя
  const winner = Object.values(gameState.players).reduce((prev, current) => {
    return (prev.score > current.score) ? prev : current;
  });
  
  const isWinner = winner.id === playerId;
  
  return (
    <div className="game-over">
      <h2>{isWinner ? 'You Win!' : 'Game Over'}</h2>
      <div className="game-results">
        <h3>Results</h3>
        {Object.values(gameState.players).sort((a, b) => b.score - a.score).map(player => (
          <div key={`result-${player.id}`} className="player-result">
            <div className="player-name">{player.name}</div>
            <div className="player-score">Score: {player.score}</div>
          </div>
        ))}
      </div>
      <div className="game-over-buttons">
        <button onClick={onRestart}>Play Again</button>
        <button onClick={onMainMenu}>Main Menu</button>
      </div>
    </div>
  );
};

// Компонент для отображения паузы
const GamePause: React.FC<{
  onResume: () => void;
  onMainMenu: () => void;
}> = ({ onResume, onMainMenu }) => {
  return (
    <div className="game-pause">
      <h2>Game Paused</h2>
      <div className="pause-buttons">
        <button onClick={onResume}>Resume</button>
        <button onClick={onMainMenu}>Main Menu</button>
      </div>
    </div>
  );
};

// Основной компонент игры
const Game: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [playerId, setPlayerId] = useState<number>(1);
  const [gameScreen, setGameScreen] = useState<'menu' | 'settings' | 'game' | 'pause' | 'gameover'>('menu');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [settings, setSettings] = useState({
    playerName: 'Player 1',
    volume: 50,
    musicEnabled: true,
    soundEnabled: true,
    difficulty: 'medium'
  });
  
  // Инициализация WebSocket соединения
  useEffect(() => {
    if (gameScreen === 'game' && !socket) {
      const newSocket = new WebSocket('ws://localhost:8000/ws');
      
      newSocket.onopen = () => {
        console.log('WebSocket connection established');
      };
      
      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'game_state') {
          setGameState(data.game_state);
        }
      };
      
      newSocket.onclose = () => {
        console.log('WebSocket connection closed');
      };
      
      setSocket(newSocket);
      
      return () => {
        newSocket.close();
      };
    }
  }, [gameScreen, socket]);
  
  // Обработка начала игры
  const handleStartGame = async (mode: GameMode) => {
    try {
      const response = await fetch('http://localhost:8000/game/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mode: mode,
          player_name: settings.playerName,
          difficulty: settings.difficulty
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlayerId(data.player_id);
        setGameScreen('game');
      } else {
        console.error('Failed to start game');
      }
    } catch (error) {
      console.error('Error starting game:', error);
    }
  };
  
  // Обработка движения тетромино
  const handleMove = (moveType: string, x: number, y: number, rotation: number) => {
    if (socket) {
      socket.send(JSON.stringify({
        type: 'move',
        move_type: moveType,
        x: x,
        y: y,
        rotation: rotation
      }));
    }
  };
  
  // Обработка использования заклинания
  const handleSpellCast = (spell: SpellType, targetId: number) => {
    if (socket) {
      socket.send(JSON.stringify({
        type: 'spell',
        spell_type: spell,
        target_id: targetId
      }));
    }
  };
  
  // Обработка сохранения настроек
  const handleSaveSettings = (newSettings: any) => {
    setSettings(newSettings);
    setGameScreen('menu');
  };
  
  // Обработка паузы
  const handlePause = () => {
    setGameScreen('pause');
    if (socket) {
      socket.send(JSON.stringify({
        type: 'pause'
      }));
    }
  };
  
  // Обработка возобновления игры
  const handleResume = () => {
    setGameScreen('game');
    if (socket) {
      socket.send(JSON.stringify({
        type: 'resume'
      }));
    }
  };
  
  // Обработка перезапуска игры
  const handleRestart = () => {
    if (gameState) {
      handleStartGame(gameState.gameMode);
    }
  };
  
  // Обработка возврата в главное меню
  const handleMainMenu = () => {
    setGameScreen('menu');
    if (socket) {
      socket.close();
      setSocket(null);
    }
  };
  
  // Отображение соответствующего экрана
  const renderScreen = () => {
    switch (gameScreen) {
      case 'menu':
        return (
          <GameMenu
            onStartGame={handleStartGame}
            onSettings={() => setGameScreen('settings')}
          />
        );
      case 'settings':
        return (
          <GameSettings
            onSave={handleSaveSettings}
            onCancel={() => setGameScreen('menu')}
          />
        );
      case 'game':
        return gameState ? (
          <>
            <div className="game-header">
              <div className="game-mode">{gameState.gameMode}</div>
              <div className="game-timer">{Math.floor(gameState.timer)}s</div>
              <button className="pause-button" onClick={handlePause}>Pause</button>
            </div>
            <GameBoard
              gameState={gameState}
              playerId={playerId}
              onMove={handleMove}
              onSpellCast={handleSpellCast}
            />
          </>
        ) : (
          <div className="loading">Loading game...</div>
        );
      case 'pause':
        return (
          <GamePause
            onResume={handleResume}
            onMainMenu={handleMainMenu}
          />
        );
      case 'gameover':
        return gameState ? (
          <GameOver
            gameState={gameState}
            playerId={playerId}
            onRestart={handleRestart}
            onMainMenu={handleMainMenu}
          />
        ) : (
          <div className="loading">Loading results...</div>
        );
      default:
        return null;
    }
  };
  
  return (
    <div className="game-app">
      {renderScreen()}
    </div>
  );
};

export default Game;
