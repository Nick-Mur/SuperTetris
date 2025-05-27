import React from 'react';
import { SpellType } from '../types/game';
import { SPELL_ICONS } from '../constants/game';

interface SpellDisplayProps {
  spell: SpellType;
  onClick: () => void;
  isActive: boolean;
}

export const SpellDisplay: React.FC<SpellDisplayProps> = ({ spell, onClick, isActive }) => {
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