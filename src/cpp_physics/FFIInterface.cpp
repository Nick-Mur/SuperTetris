#include "include/PhysicsEngine.h"
#include "include/FFIInterface.h"
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>
#include <mutex>

using namespace TetrisTowers;

// Глобальное хранилище обратных вызовов
static CollisionCallback_FFI g_collisionCallback = nullptr;
static std::mutex g_callbackMutex;

// Обертка для обратного вызова коллизий
void collisionCallbackWrapper(const ContactInfo& contact) {
    std::lock_guard<std::mutex> lock(g_callbackMutex);
    if (g_collisionCallback) {
        ContactInfo_FFI contactFFI;
        contactFFI.blockIdA = contact.blockIdA;
        contactFFI.blockIdB = contact.blockIdB;
        contactFFI.point.x = contact.point.x;
        contactFFI.point.y = contact.point.y;
        contactFFI.normal.x = contact.normal.x;
        contactFFI.normal.y = contact.normal.y;
        contactFFI.penetration = contact.penetration;
        
        g_collisionCallback(contactFFI);
    }
}

// Реализация функций FFI

void* physics_engine_create(Vector2_FFI gravity, int iterations) {
    Vector2 gravityVec(gravity.x, gravity.y);
    return new PhysicsEngine(gravityVec, iterations);
}

void physics_engine_destroy(void* engine) {
    if (engine) {
        delete static_cast<PhysicsEngine*>(engine);
    }
}

void physics_engine_set_gravity(void* engine, Vector2_FFI gravity) {
    if (engine) {
        Vector2 gravityVec(gravity.x, gravity.y);
        static_cast<PhysicsEngine*>(engine)->setGravity(gravityVec);
    }
}

Vector2_FFI physics_engine_get_gravity(void* engine) {
    Vector2_FFI result = {0, 0};
    if (engine) {
        Vector2 gravity = static_cast<PhysicsEngine*>(engine)->getGravity();
        result.x = gravity.x;
        result.y = gravity.y;
    }
    return result;
}

void physics_engine_set_iterations(void* engine, int iterations) {
    if (engine) {
        static_cast<PhysicsEngine*>(engine)->setIterations(iterations);
    }
}

int physics_engine_get_iterations(void* engine) {
    if (engine) {
        return static_cast<PhysicsEngine*>(engine)->getIterations();
    }
    return 0;
}

void physics_engine_set_collision_callback(void* engine, CollisionCallback_FFI callback) {
    if (engine) {
        std::lock_guard<std::mutex> lock(g_callbackMutex);
        g_collisionCallback = callback;
        
        if (callback) {
            static_cast<PhysicsEngine*>(engine)->setCollisionCallback(collisionCallbackWrapper);
        } else {
            static_cast<PhysicsEngine*>(engine)->setCollisionCallback(nullptr);
        }
    }
}

void physics_engine_update(void* engine, float deltaTime) {
    if (engine) {
        static_cast<PhysicsEngine*>(engine)->update(deltaTime);
    }
}

void physics_engine_start_simulation(void* engine, float fixedTimeStep) {
    if (engine) {
        static_cast<PhysicsEngine*>(engine)->startSimulation(fixedTimeStep);
    }
}

void physics_engine_stop_simulation(void* engine) {
    if (engine) {
        static_cast<PhysicsEngine*>(engine)->stopSimulation();
    }
}

int physics_engine_is_simulation_running(void* engine) {
    if (engine) {
        return static_cast<PhysicsEngine*>(engine)->isSimulationRunning() ? 1 : 0;
    }
    return 0;
}

int physics_engine_create_block(void* engine, Vector2_FFI position, Vector2_FFI size, float angle, PhysicsMaterial_FFI material, int isStatic) {
    if (engine) {
        Vector2 posVec(position.x, position.y);
        Vector2 sizeVec(size.x, size.y);
        PhysicsMaterial mat(material.density, material.restitution, material.friction, material.isSensor != 0);
        
        return static_cast<PhysicsEngine*>(engine)->createBlock(posVec, sizeVec, angle, mat, isStatic != 0);
    }
    return -1;
}

int* physics_engine_create_tetris_block(void* engine, int type, Vector2_FFI position, float blockSize, float angle, PhysicsMaterial_FFI material, int* count) {
    if (engine && count) {
        Vector2 posVec(position.x, position.y);
        PhysicsMaterial mat(material.density, material.restitution, material.friction, material.isSensor != 0);
        
        std::vector<int> blockIds = static_cast<PhysicsEngine*>(engine)->createTetrisBlock(
            static_cast<BlockType>(type), posVec, blockSize, angle, mat);
        
        *count = static_cast<int>(blockIds.size());
        if (*count > 0) {
            int* result = new int[*count];
            for (int i = 0; i < *count; ++i) {
                result[i] = blockIds[i];
            }
            return result;
        }
    }
    
    if (count) *count = 0;
    return nullptr;
}

int physics_engine_remove_block(void* engine, int blockId) {
    if (engine) {
        return static_cast<PhysicsEngine*>(engine)->removeBlock(blockId) ? 1 : 0;
    }
    return 0;
}

int physics_engine_check_collision(void* engine, int blockIdA, int blockIdB) {
    if (engine) {
        return static_cast<PhysicsEngine*>(engine)->checkCollision(blockIdA, blockIdB) ? 1 : 0;
    }
    return 0;
}

int physics_engine_is_point_in_block(void* engine, int blockId, Vector2_FFI point) {
    if (engine) {
        Vector2 pointVec(point.x, point.y);
        return static_cast<PhysicsEngine*>(engine)->isPointInBlock(blockId, pointVec) ? 1 : 0;
    }
    return 0;
}

int* physics_engine_query_aabb(void* engine, Vector2_FFI lowerBound, Vector2_FFI upperBound, int* count) {
    if (engine && count) {
        Vector2 lbVec(lowerBound.x, lowerBound.y);
        Vector2 ubVec(upperBound.x, upperBound.y);
        
        std::vector<int> blockIds = static_cast<PhysicsEngine*>(engine)->queryAABB(lbVec, ubVec);
        
        *count = static_cast<int>(blockIds.size());
        if (*count > 0) {
            int* result = new int[*count];
            for (int i = 0; i < *count; ++i) {
                result[i] = blockIds[i];
            }
            return result;
        }
    }
    
    if (count) *count = 0;
    return nullptr;
}

int physics_engine_find_closest_block(void* engine, Vector2_FFI point, float maxDistance) {
    if (engine) {
        Vector2 pointVec(point.x, point.y);
        return static_cast<PhysicsEngine*>(engine)->findClosestBlock(pointVec, maxDistance);
    }
    return -1;
}

void physics_engine_apply_explosion(void* engine, Vector2_FFI center, float radius, float force) {
    if (engine) {
        Vector2 centerVec(center.x, center.y);
        static_cast<PhysicsEngine*>(engine)->applyExplosion(centerVec, radius, force);
    }
}

void physics_engine_apply_wind(void* engine, Vector2_FFI direction, float strength) {
    if (engine) {
        Vector2 dirVec(direction.x, direction.y);
        static_cast<PhysicsEngine*>(engine)->applyWind(dirVec, strength);
    }
}

Vector2_FFI physics_block_get_position(void* engine, int blockId) {
    Vector2_FFI result = {0, 0};
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 pos = block->getPosition();
            result.x = pos.x;
            result.y = pos.y;
        }
    }
    return result;
}

void physics_block_set_position(void* engine, int blockId, Vector2_FFI position) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 posVec(position.x, position.y);
            block->setPosition(posVec);
        }
    }
}

float physics_block_get_angle(void* engine, int blockId) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            return block->getAngle();
        }
    }
    return 0.0f;
}

void physics_block_set_angle(void* engine, int blockId, float angle) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            block->setAngle(angle);
        }
    }
}

Vector2_FFI physics_block_get_linear_velocity(void* engine, int blockId) {
    Vector2_FFI result = {0, 0};
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 vel = block->getLinearVelocity();
            result.x = vel.x;
            result.y = vel.y;
        }
    }
    return result;
}

void physics_block_set_linear_velocity(void* engine, int blockId, Vector2_FFI velocity) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 velVec(velocity.x, velocity.y);
            block->setLinearVelocity(velVec);
        }
    }
}

float physics_block_get_angular_velocity(void* engine, int blockId) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            return block->getAngularVelocity();
        }
    }
    return 0.0f;
}

void physics_block_set_angular_velocity(void* engine, int blockId, float velocity) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            block->setAngularVelocity(velocity);
        }
    }
}

void physics_block_apply_force(void* engine, int blockId, Vector2_FFI force, Vector2_FFI point) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 forceVec(force.x, force.y);
            Vector2 pointVec(point.x, point.y);
            block->applyForce(forceVec, pointVec);
        }
    }
}

void physics_block_apply_impulse(void* engine, int blockId, Vector2_FFI impulse, Vector2_FFI point) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 impulseVec(impulse.x, impulse.y);
            Vector2 pointVec(point.x, point.y);
            block->applyImpulse(impulseVec, pointVec);
        }
    }
}

void physics_block_apply_torque(void* engine, int blockId, float torque) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            block->applyTorque(torque);
        }
    }
}

Vector2_FFI physics_block_get_size(void* engine, int blockId) {
    Vector2_FFI result = {0, 0};
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            Vector2 size = block->getSize();
            result.x = size.x;
            result.y = size.y;
        }
    }
    return result;
}

float physics_block_get_mass(void* engine, int blockId) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            return block->getMass();
        }
    }
    return 0.0f;
}

float physics_block_get_inertia(void* engine, int blockId) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            return block->getInertia();
        }
    }
    return 0.0f;
}

int physics_block_is_static(void* engine, int blockId) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            return block->isStatic() ? 1 : 0;
        }
    }
    return 0;
}

void physics_block_set_static(void* engine, int blockId, int isStatic) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            block->setStatic(isStatic != 0);
        }
    }
}

PhysicsMaterial_FFI physics_block_get_material(void* engine, int blockId) {
    PhysicsMaterial_FFI result = {1.0f, 0.1f, 0.3f, 0};
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            PhysicsMaterial mat = block->getMaterial();
            result.density = mat.density;
            result.restitution = mat.restitution;
            result.friction = mat.friction;
            result.isSensor = mat.isSensor ? 1 : 0;
        }
    }
    return result;
}

void physics_block_set_material(void* engine, int blockId, PhysicsMaterial_FFI material) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            PhysicsMaterial mat(material.density, material.restitution, material.friction, material.isSensor != 0);
            block->setMaterial(mat);
        }
    }
}

int physics_block_is_active(void* engine, int blockId) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            return block->isActive() ? 1 : 0;
        }
    }
    return 0;
}

void physics_block_set_active(void* engine, int blockId, int isActive) {
    if (engine) {
        PhysicsBlock* block = static_cast<PhysicsEngine*>(engine)->getBlock(blockId);
        if (block) {
            block->setActive(isActive != 0);
        }
    }
}

// Глобальное хранилище для строк JSON
static std::string g_lastJsonString;
static std::mutex g_jsonMutex;

const char* physics_engine_serialize_to_json(void* engine) {
    if (engine) {
        std::lock_guard<std::mutex> lock(g_jsonMutex);
        g_lastJsonString = static_cast<PhysicsEngine*>(engine)->serializeToJson();
        return g_lastJsonString.c_str();
    }
    return nullptr;
}

int physics_engine_deserialize_from_json(void* engine, const char* json) {
    if (engine && json) {
        return static_cast<PhysicsEngine*>(engine)->deserializeFromJson(json) ? 1 : 0;
    }
    return 0;
}

void physics_free_string(const char* str) {
    // Строки хранятся в глобальной переменной, поэтому не требуют освобождения
    // Эта функция предоставляется для совместимости с другими языками
}

void physics_free_int_array(int* array) {
    if (array) {
        delete[] array;
    }
}
