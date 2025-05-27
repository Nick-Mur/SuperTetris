import React, { useEffect, useState, useRef } from 'react';
import { Stage, Layer } from 'react-konva';
import { GameState, SpellType } from '../types/game';
import { TetrominoDisplay } from './TetrominoDisplay';
import { BlockDisplay } from './BlockDisplay';
import { SpellDisplay } from './SpellDisplay';

interface GameBoardProps {
  gameState: GameState;
  playerId: string;
  onMove: (moveType: string, x: number, y: number, rotation: number) => void;
  onSpellCast: (spell: SpellType, targetId: number) => void;
}

export const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  playerId,
  onMove,
  onSpellCast
}) => {
  const [selectedSpell, setSelectedSpell] = useState<SpellType | null>(null);
  const [selectedTarget, setSelectedTarget] = useState<number | null>(null);
  const [blockSize, setBlockSize] = useState(30);
  const boardRef = useRef<HTMLDivElement>(null);
  
  const currentPlayer = gameState.players[playerId];
  
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
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!currentPlayer?.currentTetromino) return;
      
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
          onMove('hard_drop', x, y, rotation);
          break;
        case 'c':
          onMove('hold', x, y, rotation);
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentPlayer, onMove]);
  
  const handleSpellClick = (spell: SpellType) => {
    setSelectedSpell(spell);
  };
  
  const handleTargetClick = (targetId: number) => {
    if (selectedSpell) {
      onSpellCast(selectedSpell, targetId);
      setSelectedSpell(null);
      setSelectedTarget(null);
    }
  };
  
  if (!currentPlayer) {
    return <div>Loading...</div>;
  }
  
  return (
    <div ref={boardRef} className="game-board">
      <Stage width={boardRef.current?.clientWidth || 300} height={boardRef.current?.clientHeight || 600}>
        <Layer>
          {currentPlayer.towerBlocks.map((block) => (
            <BlockDisplay key={block.id} block={block} blockSize={blockSize} />
          ))}
          {currentPlayer.currentTetromino && (
            <TetrominoDisplay
              tetromino={currentPlayer.currentTetromino}
              blockSize={blockSize}
            />
          )}
        </Layer>
      </Stage>
      <div className="spells-container">
        {currentPlayer.spells.map((spell) => (
          <SpellDisplay
            key={spell}
            spell={spell}
            onClick={() => handleSpellClick(spell)}
            isActive={selectedSpell === spell}
          />
        ))}
      </div>
    </div>
  );
}; 