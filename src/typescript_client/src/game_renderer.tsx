import React, { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { Application, Container, Graphics, Sprite, Text, AnimatedSprite } from 'pixi.js';
import { TetrominoType, Direction, RotationDirection, SpellType, GameMode } from './types/game';

/**
 * GameRenderer - Клиентская часть для игры Tetris с элементами Tricky Towers
 * Реализовано на TypeScript с использованием PixiJS для рендеринга
 */

// Интерфейсы для типов данных
interface Position {
  x: number;
  y: number;
}

interface Size {
  width: number;
  height: number;
}

interface Block {
  id: number;
  position: Position;
  size: Size;
  rotation: number;
  color: number;
  properties: BlockProperties;
}

interface BlockProperties {
  isStatic: boolean;
  density: number;
  friction: number;
  restitution: number;
}

interface Tetromino {
  shape: TetrominoType;
  position: Position;
  rotation: number;
  blocks: Block[];
}

interface PlayerState {
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
  players: Record<number, PlayerState>;
  gameMode: GameMode;
  currentTurn: number;
  gameStatus: string;
  timer: number;
}

// Константы
const CELL_SIZE = 30;
const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const COLORS = {
  [TetrominoType.I]: 0x00FFFF, // Голубой
  [TetrominoType.J]: 0x0000FF, // Синий
  [TetrominoType.L]: 0xFFA500, // Оранжевый
  [TetrominoType.O]: 0xFFFF00, // Желтый
  [TetrominoType.S]: 0x00FF00, // Зеленый
  [TetrominoType.T]: 0x800080, // Фиолетовый
  [TetrominoType.Z]: 0xFF0000, // Красный
};

// Класс для рендеринга игры
export class GameRenderer {
  private app: Application;
  private gameContainer: Container;
  private boardContainer: Container;
  private uiContainer: Container;
  private blockSprites: Map<number, Graphics>;
  private playerContainers: Map<number, Container>;
  private nextTetrominoContainers: Map<number, Container>;
  private heldTetrominoContainers: Map<number, Container>;
  private spellContainers: Map<number, Container>;
  private scoreTexts: Map<number, Text>;
  private healthTexts: Map<number, Text>;
  private timerText: Text;
  private gameState: GameState | null = null;
  private spellAnimations: Map<string, PIXI.AnimatedSprite>;
  private textures: Record<string, PIXI.Texture>;

  constructor(canvas: HTMLCanvasElement) {
    // Инициализация PIXI Application
    this.app = new Application({
      view: canvas as HTMLCanvasElement,
      width: 800,
      height: 600,
      backgroundColor: 0x1099bb,
      resolution: window.devicePixelRatio || 1,
    });

    // Создание контейнеров
    this.gameContainer = new Container();
    this.boardContainer = new Container();
    this.uiContainer = new Container();
    this.app.stage.addChild(this.gameContainer);
    this.gameContainer.addChild(this.boardContainer);
    this.gameContainer.addChild(this.uiContainer);

    // Инициализация коллекций
    this.blockSprites = new Map();
    this.playerContainers = new Map();
    this.nextTetrominoContainers = new Map();
    this.heldTetrominoContainers = new Map();
    this.spellContainers = new Map();
    this.scoreTexts = new Map();
    this.healthTexts = new Map();
    this.spellAnimations = new Map();
    this.textures = {};

    // Создание текста таймера
    this.timerText = new Text('Time: 0', {
      fontFamily: 'Arial',
      fontSize: 24,
      fill: 0xffffff,
    });
    this.timerText.position.set(10, 10);
    this.uiContainer.addChild(this.timerText);

    // Загрузка текстур
    this.loadTextures();

    // Запуск игрового цикла
    this.app.ticker.add(() => this.gameLoop());
  }

  // Загрузка текстур
  private loadTextures(): void {
    // Загрузка текстур для блоков
    Object.values(TetrominoType).forEach((type) => {
      this.textures[`block_${type}`] = PIXI.Texture.from(`assets/blocks/${(type as string).toLowerCase()}.png`);
    });

    // Загрузка текстур для заклинаний
    Object.values(SpellType).forEach((type) => {
      this.textures[`spell_${type}`] = PIXI.Texture.from(`assets/spells/${(type as string).toLowerCase()}.png`);
    });

    // Загрузка текстур для анимаций заклинаний
    Object.values(SpellType).forEach((type) => {
      const frames = [];
      for (let i = 0; i < 5; i++) {
        frames.push(PIXI.Texture.from(`assets/spell_animations/${(type as string).toLowerCase()}_${i}.png`));
      }
      // Создаем анимированный спрайт из текстур
      this.spellAnimations.set(type, PIXI.AnimatedSprite.fromFrames(frames));
      this.gameContainer.addChild(this.spellAnimations.get(type)!);
    });
  }

  // Обновление состояния игры
  public updateGameState(gameState: GameState): void {
    this.gameState = gameState;
  }

  // Игровой цикл
  private gameLoop(): void {
    if (!this.gameState) return;

    // Обновление таймера
    this.timerText.text = `Time: ${Math.floor(this.gameState.timer)}`;

    // Обновление состояния игроков
    Object.values(this.gameState.players).forEach((player) => {
      this.updatePlayer(player);
    });
  }

  // Обновление состояния игрока
  private updatePlayer(player: PlayerState): void {
    // Создание контейнера для игрока, если его еще нет
    if (!this.playerContainers.has(player.id)) {
      this.createPlayerContainer(player);
    }

    // Обновление блоков башни
    this.updateTowerBlocks(player);

    // Обновление текущего тетромино
    this.updateCurrentTetromino(player);

    // Обновление следующих тетромино
    this.updateNextTetrominos(player);

    // Обновление удерживаемого тетромино
    this.updateHeldTetromino(player);

    // Обновление заклинаний
    this.updateSpells(player);

    // Обновление очков
    this.updateScore(player);

    // Обновление здоровья
    this.updateHealth(player);
  }

  // Создание контейнера для игрока
  private createPlayerContainer(player: PlayerState): void {
    const container = new Container();
    const playerIndex = this.playerContainers.size;
    const xOffset = playerIndex * (BOARD_WIDTH * CELL_SIZE + 150);
    
    container.position.set(xOffset, 50);
    this.gameContainer.addChild(container);
    this.playerContainers.set(player.id, container);

    // Создание контейнера для следующих тетромино
    const nextContainer = new Container();
    nextContainer.position.set(BOARD_WIDTH * CELL_SIZE + 20, 0);
    container.addChild(nextContainer);
    this.nextTetrominoContainers.set(player.id, nextContainer);

    // Создание контейнера для удерживаемого тетромино
    const heldContainer = new Container();
    heldContainer.position.set(BOARD_WIDTH * CELL_SIZE + 20, 200);
    container.addChild(heldContainer);
    this.heldTetrominoContainers.set(player.id, heldContainer);

    // Создание контейнера для заклинаний
    const spellContainer = new Container();
    spellContainer.position.set(BOARD_WIDTH * CELL_SIZE + 20, 300);
    container.addChild(spellContainer);
    this.spellContainers.set(player.id, spellContainer);

    // Создание текста для очков
    const scoreText = new Text(`Score: ${player.score}`, {
      fontFamily: 'Arial',
      fontSize: 18,
      fill: 0xffffff,
    });
    scoreText.position.set(BOARD_WIDTH * CELL_SIZE + 20, 400);
    container.addChild(scoreText);
    this.scoreTexts.set(player.id, scoreText);

    // Создание текста для здоровья
    const healthText = new Text(`Health: ${player.health}`, {
      fontFamily: 'Arial',
      fontSize: 18,
      fill: 0xffffff,
    });
    healthText.position.set(BOARD_WIDTH * CELL_SIZE + 20, 430);
    container.addChild(healthText);
    this.healthTexts.set(player.id, healthText);

    // Создание игрового поля
    const board = new Graphics();
    board.beginFill(0x000000, 0.5);
    board.drawRect(0, 0, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE);
    board.endFill();
    container.addChild(board);

    // Создание сетки
    const grid = new Graphics();
    grid.lineStyle(1, 0x333333, 0.5);
    for (let i = 0; i <= BOARD_WIDTH; i++) {
      grid.moveTo(i * CELL_SIZE, 0);
      grid.lineTo(i * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE);
    }
    for (let i = 0; i <= BOARD_HEIGHT; i++) {
      grid.moveTo(0, i * CELL_SIZE);
      grid.lineTo(BOARD_WIDTH * CELL_SIZE, i * CELL_SIZE);
    }
    container.addChild(grid);

    // Добавление имени игрока
    const nameText = new Text(player.name, {
      fontFamily: 'Arial',
      fontSize: 20,
      fill: 0xffffff,
    });
    nameText.position.set(0, -30);
    container.addChild(nameText);
  }

  // Обновление блоков башни
  private updateTowerBlocks(player: PlayerState): void {
    const container = this.playerContainers.get(player.id);
    if (!container) return;

    // Удаление старых блоков
    this.blockSprites.forEach((sprite, id) => {
      const blockExists = player.towerBlocks.some(block => block.id === id);
      if (!blockExists) {
        sprite.parent.removeChild(sprite);
        this.blockSprites.delete(id);
      }
    });

    // Добавление новых блоков
    player.towerBlocks.forEach(block => {
      if (!this.blockSprites.has(block.id)) {
        const sprite = this.createBlockSprite(block);
        container.addChild(sprite);
        this.blockSprites.set(block.id, sprite);
      } else {
        // Обновление существующего блока
        const sprite = this.blockSprites.get(block.id)!;
        sprite.position.set(
          block.position.x * CELL_SIZE,
          block.position.y * CELL_SIZE
        );
        sprite.rotation = block.rotation;
        sprite.scale.set(
          block.size.width,
          block.size.height
        );
      }
    });
  }

  // Создание спрайта блока
  private createBlockSprite(block: Block): Graphics {
    const sprite = new Graphics();
    sprite.beginFill(block.color);
    sprite.drawRect(0, 0, CELL_SIZE, CELL_SIZE);
    sprite.endFill();
    sprite.position.set(
      block.position.x * CELL_SIZE,
      block.position.y * CELL_SIZE
    );
    sprite.rotation = block.rotation;
    sprite.scale.set(
      block.size.width,
      block.size.height
    );
    return sprite;
  }

  // Обновление текущего тетромино
  private updateCurrentTetromino(player: PlayerState): void {
    const container = this.playerContainers.get(player.id);
    if (!container) return;

    // Удаление старого тетромино
    container.children.forEach((child: PIXI.DisplayObject) => {
      if (child.name === 'current_tetromino') {
        container.removeChild(child);
      }
    });

    // Добавление нового тетромино
    if (player.currentTetromino) {
      const tetromino = player.currentTetromino;
      const tetrominoContainer = new Container();
      tetrominoContainer.name = 'current_tetromino';

      tetromino.blocks.forEach(block => {
        const sprite = this.createBlockSprite(block);
        tetrominoContainer.addChild(sprite);
      });

      container.addChild(tetrominoContainer);
    }
  }

  // Обновление следующих тетромино
  private updateNextTetrominos(player: PlayerState): void {
    const container = this.nextTetrominoContainers.get(player.id);
    if (!container) return;

    // Очистка контейнера
    container.removeChildren();

    // Добавление заголовка
    const titleText = new Text('Next', {
      fontFamily: 'Arial',
      fontSize: 18,
      fill: 0xffffff,
    });
    titleText.position.set(0, 0);
    container.addChild(titleText);

    // Добавление следующих тетромино
    player.nextTetrominos.forEach((tetromino, index) => {
      const tetrominoContainer = new Container();
      tetrominoContainer.position.set(0, 30 + index * 80);

      // Создание миниатюры тетромино
      const miniTetromino = this.createMiniTetromino(tetromino.shape);
      tetrominoContainer.addChild(miniTetromino);

      container.addChild(tetrominoContainer);
    });
  }

  // Обновление удерживаемого тетромино
  private updateHeldTetromino(player: PlayerState): void {
    const container = this.heldTetrominoContainers.get(player.id);
    if (!container) return;

    // Очистка контейнера
    container.removeChildren();

    // Добавление заголовка
    const titleText = new Text('Hold', {
      fontFamily: 'Arial',
      fontSize: 18,
      fill: 0xffffff,
    });
    titleText.position.set(0, 0);
    container.addChild(titleText);

    // Добавление удерживаемого тетромино
    if (player.heldTetromino) {
      const tetrominoContainer = new Container();
      tetrominoContainer.position.set(0, 30);

      // Создание миниатюры тетромино
      const miniTetromino = this.createMiniTetromino(player.heldTetromino.shape);
      tetrominoContainer.addChild(miniTetromino);

      container.addChild(tetrominoContainer);
    }
  }

  // Создание миниатюры тетромино
  private createMiniTetromino(shape: TetrominoType): Container {
    const container = new Container();
    const color = COLORS[shape];
    const size = 15; // Размер блока в миниатюре

    // Определение формы тетромино
    let blocks: { x: number, y: number }[] = [];
    switch (shape) {
      case TetrominoType.I:
        blocks = [{ x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 3, y: 1 }];
        break;
      case TetrominoType.J:
        blocks = [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }];
        break;
      case TetrominoType.L:
        blocks = [{ x: 2, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }];
        break;
      case TetrominoType.O:
        blocks = [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }];
        break;
      case TetrominoType.S:
        blocks = [{ x: 1, y: 0 }, { x: 2, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }];
        break;
      case TetrominoType.T:
        blocks = [{ x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }];
        break;
      case TetrominoType.Z:
        blocks = [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 1 }];
        break;
    }

    // Создание блоков
    blocks.forEach(block => {
      const sprite = new Graphics();
      sprite.beginFill(color);
      sprite.drawRect(0, 0, size, size);
      sprite.endFill();
      sprite.position.set(block.x * size, block.y * size);
      container.addChild(sprite);
    });

    return container;
  }

  // Обновление заклинаний
  private updateSpells(player: PlayerState): void {
    const container = this.spellContainers.get(player.id);
    if (!container) return;

    // Очистка контейнера
    container.removeChildren();

    // Добавление заголовка
    const titleText = new Text('Spells', {
      fontFamily: 'Arial',
      fontSize: 18,
      fill: 0xffffff,
    });
    titleText.position.set(0, 0);
    container.addChild(titleText);

    // Добавление заклинаний
    player.spells.forEach((spell, index) => {
      const spellContainer = new Container();
      spellContainer.position.set(index * 40, 30);

      // Создание иконки заклинания
      const icon = new Graphics();
      icon.beginFill(0xffffff);
      icon.drawRect(0, 0, 30, 30);
      icon.endFill();
      
      // Добавление текста заклинания
      const text = new Text(spell.charAt(0).toUpperCase(), {
        fontFamily: 'Arial',
        fontSize: 14,
        fill: 0x000000,
      });
      text.position.set(10, 8);
      
      spellContainer.addChild(icon);
      spellContainer.addChild(text);
      container.addChild(spellContainer);
    });
  }

  // Обновление очков
  private updateScore(player: PlayerState): void {
    const scoreText = this.scoreTexts.get(player.id);
    if (scoreText) {
      scoreText.text = `Score: ${player.score}`;
    }
  }

  // Обновление здоровья
  private updateHealth(player: PlayerState): void {
    const healthText = this.healthTexts.get(player.id);
    if (healthText) {
      healthText.text = `Health: ${player.health}`;
    }
  }

  // Воспроизведение анимации заклинания
  public playSpellAnimation(spellType: SpellType, position: Position): void {
    const animation = this.spellAnimations.get(spellType);
    if (animation) {
      animation.position.set(position.x, position.y);
      animation.visible = true;
      animation.gotoAndPlay(0);
      
      // Скрытие анимации после завершения
      animation.onComplete = () => {
        animation.visible = false;
      };
    }
  }

  // Изменение размера канваса
  public resize(width: number, height: number): void {
    this.app.renderer.resize(width, height);
    
    // Центрирование игрового контейнера
    this.gameContainer.position.set(
      width / 2 - this.gameContainer.width / 2,
      height / 2 - this.gameContainer.height / 2
    );
  }

  // Уничтожение рендерера
  public destroy(): void {
    this.app.destroy(true);
  }
}

// React компонент для игры
const Game: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<GameRenderer | null>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);

  // Инициализация рендерера
  useEffect(() => {
    if (canvasRef.current && !rendererRef.current) {
      rendererRef.current = new GameRenderer(canvasRef.current);
    }

    // Обработка изменения размера окна
    const handleResize = () => {
      if (rendererRef.current) {
        rendererRef.current.resize(window.innerWidth, window.innerHeight);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    // Очистка при размонтировании
    return () => {
      window.removeEventListener('resize', handleResize);
      if (rendererRef.current) {
        rendererRef.current.destroy();
        rendererRef.current = null;
      }
    };
  }, []);

  // Обновление состояния игры
  useEffect(() => {
    if (rendererRef.current && gameState) {
      rendererRef.current.updateGameState(gameState);
    }
  }, [gameState]);

  // Обработка клавиатурного ввода
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Обработка клавиш управления
      switch (event.key) {
        case 'ArrowLeft':
          // Перемещение влево
          break;
        case 'ArrowRight':
          // Перемещение вправо
          break;
        case 'ArrowDown':
          // Перемещение вниз
          break;
        case 'ArrowUp':
          // Вращение по часовой стрелке
          break;
        case 'z':
          // Вращение против часовой стрелки
          break;
        case ' ':
          // Сброс тетромино
          break;
        case 'c':
          // Удержание тетромино
          break;
        case '1':
        case '2':
        case '3':
          // Использование заклинания
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <div className="game-container">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default Game;
