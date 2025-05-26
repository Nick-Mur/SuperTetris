#ifndef FFI_INTERFACE_H
#define FFI_INTERFACE_H

#ifdef __cplusplus
extern "C" {
#endif

// Структуры для FFI
typedef struct {
    float x;
    float y;
} Vector2_FFI;

typedef struct {
    float density;
    float restitution;
    float friction;
    int isSensor;
} PhysicsMaterial_FFI;

typedef struct {
    int blockIdA;
    int blockIdB;
    Vector2_FFI point;
    Vector2_FFI normal;
    float penetration;
} ContactInfo_FFI;

// Типы для обратных вызовов
typedef void (*CollisionCallback_FFI)(ContactInfo_FFI);

// Создание и управление физическим движком
void* physics_engine_create(Vector2_FFI gravity, int iterations);
void physics_engine_destroy(void* engine);
void physics_engine_set_gravity(void* engine, Vector2_FFI gravity);
Vector2_FFI physics_engine_get_gravity(void* engine);
void physics_engine_set_iterations(void* engine, int iterations);
int physics_engine_get_iterations(void* engine);
void physics_engine_set_collision_callback(void* engine, CollisionCallback_FFI callback);
void physics_engine_update(void* engine, float deltaTime);
void physics_engine_start_simulation(void* engine, float fixedTimeStep);
void physics_engine_stop_simulation(void* engine);
int physics_engine_is_simulation_running(void* engine);

// Создание и управление блоками
int physics_engine_create_block(void* engine, Vector2_FFI position, Vector2_FFI size, float angle, PhysicsMaterial_FFI material, int isStatic);
int* physics_engine_create_tetris_block(void* engine, int type, Vector2_FFI position, float blockSize, float angle, PhysicsMaterial_FFI material, int* count);
int physics_engine_remove_block(void* engine, int blockId);
int physics_engine_check_collision(void* engine, int blockIdA, int blockIdB);
int physics_engine_is_point_in_block(void* engine, int blockId, Vector2_FFI point);
int* physics_engine_query_aabb(void* engine, Vector2_FFI lowerBound, Vector2_FFI upperBound, int* count);
int physics_engine_find_closest_block(void* engine, Vector2_FFI point, float maxDistance);
void physics_engine_apply_explosion(void* engine, Vector2_FFI center, float radius, float force);
void physics_engine_apply_wind(void* engine, Vector2_FFI direction, float strength);

// Получение и установка свойств блоков
Vector2_FFI physics_block_get_position(void* engine, int blockId);
void physics_block_set_position(void* engine, int blockId, Vector2_FFI position);
float physics_block_get_angle(void* engine, int blockId);
void physics_block_set_angle(void* engine, int blockId, float angle);
Vector2_FFI physics_block_get_linear_velocity(void* engine, int blockId);
void physics_block_set_linear_velocity(void* engine, int blockId, Vector2_FFI velocity);
float physics_block_get_angular_velocity(void* engine, int blockId);
void physics_block_set_angular_velocity(void* engine, int blockId, float velocity);
void physics_block_apply_force(void* engine, int blockId, Vector2_FFI force, Vector2_FFI point);
void physics_block_apply_impulse(void* engine, int blockId, Vector2_FFI impulse, Vector2_FFI point);
void physics_block_apply_torque(void* engine, int blockId, float torque);
Vector2_FFI physics_block_get_size(void* engine, int blockId);
float physics_block_get_mass(void* engine, int blockId);
float physics_block_get_inertia(void* engine, int blockId);
int physics_block_is_static(void* engine, int blockId);
void physics_block_set_static(void* engine, int blockId, int isStatic);
PhysicsMaterial_FFI physics_block_get_material(void* engine, int blockId);
void physics_block_set_material(void* engine, int blockId, PhysicsMaterial_FFI material);
int physics_block_is_active(void* engine, int blockId);
void physics_block_set_active(void* engine, int blockId, int isActive);

// Сериализация
const char* physics_engine_serialize_to_json(void* engine);
int physics_engine_deserialize_from_json(void* engine, const char* json);

// Освобождение памяти
void physics_free_string(const char* str);
void physics_free_int_array(int* array);

#ifdef __cplusplus
}
#endif

#endif // FFI_INTERFACE_H
