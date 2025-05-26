import pytest
import uuid
import asyncio
from ..physics.manager import PhysicsManager

@pytest.fixture
def physics_manager():
    return PhysicsManager()

@pytest.mark.asyncio
async def test_add_block(physics_manager):
    block_id = uuid.uuid4()
    position = (0.0, 0.0)
    rotation = 0.0
    await physics_manager.add_block(block_id, position, rotation)
    assert block_id in physics_manager.blocks
    assert physics_manager.blocks[block_id]["position"] == position
    assert physics_manager.blocks[block_id]["rotation"] == rotation

@pytest.mark.asyncio
async def test_remove_block(physics_manager):
    block_id = uuid.uuid4()
    position = (0.0, 0.0)
    rotation = 0.0
    await physics_manager.add_block(block_id, position, rotation)
    await physics_manager.remove_block(block_id)
    assert block_id not in physics_manager.blocks

@pytest.mark.asyncio
async def test_update_block_position(physics_manager):
    block_id = uuid.uuid4()
    initial_position = (0.0, 0.0)
    new_position = (1.0, 1.0)
    rotation = 0.0
    await physics_manager.add_block(block_id, initial_position, rotation)
    await physics_manager.update_block_position(block_id, new_position)
    assert physics_manager.blocks[block_id]["position"] == new_position

@pytest.mark.asyncio
async def test_update_block_rotation(physics_manager):
    block_id = uuid.uuid4()
    position = (0.0, 0.0)
    initial_rotation = 0.0
    new_rotation = 90.0
    await physics_manager.add_block(block_id, position, initial_rotation)
    await physics_manager.update_block_rotation(block_id, new_rotation)
    assert physics_manager.blocks[block_id]["rotation"] == new_rotation

@pytest.mark.asyncio
async def test_apply_force(physics_manager):
    block_id = uuid.uuid4()
    position = (0.0, 0.0)
    rotation = 0.0
    force = (1.0, 1.0)
    await physics_manager.add_block(block_id, position, rotation)
    await physics_manager.apply_force(block_id, force)
    assert physics_manager.blocks[block_id]["velocity"] == force

@pytest.mark.asyncio
async def test_apply_torque(physics_manager):
    block_id = uuid.uuid4()
    position = (0.0, 0.0)
    rotation = 0.0
    torque = 1.0
    await physics_manager.add_block(block_id, position, rotation)
    await physics_manager.apply_torque(block_id, torque)
    assert physics_manager.blocks[block_id]["angular_velocity"] == torque

@pytest.mark.asyncio
async def test_physics_update_loop(physics_manager):
    block_id = uuid.uuid4()
    position = (0.0, 0.0)
    rotation = 0.0
    await physics_manager.add_block(block_id, position, rotation)
    await physics_manager.start()
    await asyncio.sleep(0.1)
    await physics_manager.stop()
    assert not physics_manager.running
    assert physics_manager.blocks[block_id]["position"] != position  # Позиция должна измениться из-за гравитации 