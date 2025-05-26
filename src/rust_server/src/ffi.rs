#[repr(C)]
pub struct Vec2 {
    pub x: f32,
    pub y: f32,
}

#[repr(C)]
pub struct BlockInfo {
    pub id: i32,
    pub position: Vec2,
    pub angle: f32,
    pub linear_velocity: Vec2,
    pub angular_velocity: f32,
    pub width: f32,
    pub height: f32,
    pub is_static: bool,
    pub is_active: bool,
}

#[repr(C)]
pub struct CollisionInfo {
    pub block_a_id: i32,
    pub block_b_id: i32,
    pub point: Vec2,
    pub normal: Vec2,
    pub impulse: f32,
}

extern "C" {
    // Physics Engine Management
    pub fn physics_engine_create() -> *mut std::ffi::c_void;
    pub fn physics_engine_destroy(engine: *mut std::ffi::c_void);
    pub fn physics_engine_step(engine: *mut std::ffi::c_void, time_step: f32);
    pub fn physics_engine_set_gravity(engine: *mut std::ffi::c_void, gravity: Vec2);
    pub fn physics_engine_get_gravity(engine: *mut std::ffi::c_void) -> Vec2;
    pub fn physics_engine_set_world_bounds(engine: *mut std::ffi::c_void, min: Vec2, max: Vec2);
    pub fn physics_engine_get_collision_count(engine: *mut std::ffi::c_void) -> usize;
    pub fn physics_engine_get_collisions(engine: *mut std::ffi::c_void, buffer: *mut CollisionInfo, buffer_size: usize) -> usize;

    // Block Management
    pub fn physics_engine_create_block(
        engine: *mut std::ffi::c_void,
        position: Vec2,
        width: f32,
        height: f32,
        angle: f32,
        density: f32,
        friction: f32,
        restitution: f32,
        is_static: bool,
    ) -> i32;
    pub fn physics_engine_remove_block(engine: *mut std::ffi::c_void, block_id: i32) -> bool;
    pub fn physics_engine_get_block_info(engine: *mut std::ffi::c_void, block_id: i32, info: *mut BlockInfo) -> bool;
    pub fn physics_engine_get_all_block_ids(engine: *mut std::ffi::c_void, buffer: *mut i32, buffer_size: usize) -> usize;
    pub fn physics_engine_get_block_count(engine: *mut std::ffi::c_void) -> usize;

    // Block Manipulation
    pub fn physics_engine_set_block_position(engine: *mut std::ffi::c_void, block_id: i32, position: Vec2) -> bool;
    pub fn physics_engine_set_block_angle(engine: *mut std::ffi::c_void, block_id: i32, angle: f32) -> bool;
    pub fn physics_engine_set_block_linear_velocity(engine: *mut std::ffi::c_void, block_id: i32, velocity: Vec2) -> bool;
    pub fn physics_engine_set_block_angular_velocity(engine: *mut std::ffi::c_void, block_id: i32, velocity: f32) -> bool;
    pub fn physics_engine_apply_force(engine: *mut std::ffi::c_void, block_id: i32, force: Vec2, point: Vec2) -> bool;
    pub fn physics_engine_apply_torque(engine: *mut std::ffi::c_void, block_id: i32, torque: f32) -> bool;
    pub fn physics_engine_apply_linear_impulse(engine: *mut std::ffi::c_void, block_id: i32, impulse: Vec2, point: Vec2) -> bool;
    pub fn physics_engine_apply_angular_impulse(engine: *mut std::ffi::c_void, block_id: i32, impulse: f32) -> bool;
    pub fn physics_engine_set_block_active(engine: *mut std::ffi::c_void, block_id: i32, active: bool) -> bool;
    pub fn physics_engine_set_block_static(engine: *mut std::ffi::c_void, block_id: i32, is_static: bool) -> bool;
    pub fn physics_engine_set_block_density(engine: *mut std::ffi::c_void, block_id: i32, density: f32) -> bool;
    pub fn physics_engine_set_block_friction(engine: *mut std::ffi::c_void, block_id: i32, friction: f32) -> bool;
    pub fn physics_engine_set_block_restitution(engine: *mut std::ffi::c_void, block_id: i32, restitution: f32) -> bool;

    // Collision Detection
    pub fn physics_engine_check_collision(engine: *mut std::ffi::c_void, block_a_id: i32, block_b_id: i32) -> bool;
    pub fn physics_engine_query_aabb(engine: *mut std::ffi::c_void, min: Vec2, max: Vec2, buffer: *mut i32, buffer_size: usize) -> usize;
    pub fn physics_engine_raycast(engine: *mut std::ffi::c_void, start: Vec2, end: Vec2, buffer: *mut i32, buffer_size: usize) -> usize;
}

