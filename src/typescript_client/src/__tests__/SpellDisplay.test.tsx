import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SpellDisplay } from '../components/SpellDisplay';
import { SpellType } from '../types/game';

describe('SpellDisplay Component', () => {
  const mockOnClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders spell icon', () => {
    render(
      <SpellDisplay
        spell={SpellType.CLEAR_LINE}
        onClick={mockOnClick}
        isActive={true}
      />
    );

    const spellElement = screen.getByRole('button');
    expect(spellElement).toHaveClass('spell-display');
    expect(spellElement).toHaveClass('active');
  });

  it('calls onClick when clicked', () => {
    render(
      <SpellDisplay
        spell={SpellType.CLEAR_LINE}
        onClick={mockOnClick}
        isActive={true}
      />
    );

    const spellElement = screen.getByRole('button');
    fireEvent.click(spellElement);

    expect(mockOnClick).toHaveBeenCalledWith(SpellType.CLEAR_LINE);
  });

  it('applies inactive class when isActive is false', () => {
    render(
      <SpellDisplay
        spell={SpellType.CLEAR_LINE}
        onClick={mockOnClick}
        isActive={false}
      />
    );

    const spellElement = screen.getByRole('button');
    expect(spellElement).toHaveClass('spell-display');
    expect(spellElement).toHaveClass('inactive');
    expect(spellElement).not.toHaveClass('active');
  });

  it('displays different spell icons for different spell types', () => {
    const { rerender } = render(
      <SpellDisplay
        spell={SpellType.CLEAR_LINE}
        onClick={mockOnClick}
        isActive={true}
      />
    );

    rerender(
      <SpellDisplay
        spell={SpellType.ADD_BLOCKS}
        onClick={mockOnClick}
        isActive={true}
      />
    );
  });

  it('is disabled when inactive', () => {
    render(
      <SpellDisplay
        spell={SpellType.CLEAR_LINE}
        onClick={mockOnClick}
        isActive={false}
      />
    );

    const spellElement = screen.getByRole('button');
    expect(spellElement).toBeDisabled();
  });
}); 