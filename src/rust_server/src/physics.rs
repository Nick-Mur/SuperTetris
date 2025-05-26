use std::path::Path;
use std::fs;
use std::sync::Arc;
use anyhow::{Result, Context};
use serde::{Serialize, Deserialize};
use log::{info, error, debug};
use tokio::sync::RwLock;
use libloading::{Library, Symbol};
use std::ffi::{CString, c_void, c_char, c_int, c_float};

/// Конфигурация физического движка
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhysicsConfig {
    /// Путь к библиотеке физического движка
    pub library_path: String,
    /// Гравитация по оси X
    pub gravity_x: f32,
    /// Гравитация по оси Y
    pub gravity_y: f32,
    /// Количество итераций для разрешения коллизий
    pub iterations: i32,
    /// Фиксированный временной шаг для симуляции
    pub fixed_time_step: f32,
    /// Включить автоматическую симуляцию в отдельном потоке
    pub auto_simulation: bool,
}

impl Default for PhysicsConfig {
    fn default() -> Self {
        Self {
            library_path: "lib/libtetris_physics.so".to_string(),
            gravity_x: 0.0,
            gravity_y: -9.8,
            iterations: 10,
            fixed_time_step: 1.0 / 60.0,
            auto_simulation: true,
        }
    }
}

/// Структура для работы с физическим движком через FFI
pub struct PhysicsManager {
    /// Конфигурация физического движка
    config: PhysicsConfig,
    /// Загруженная библиотека
    library: Arc<RwLock<Option<Library>>>,
    /// Указатель на экземпляр физического движка
    engine_ptr: Arc<RwLock<Option<*mut c_void>>>,
    /// Флаг работы менеджера
    running: Arc<RwLock<bool>>,
}

/// Структура для представления вектора в 2D пространстве
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct Vector2FFI {
    pub x: f32,
    pub y: f32,
}

/// Структура для представления материала физического объекта
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct PhysicsMaterialFFI {
    pub density: f32,
    pub restitution: f32,
    pub friction: f32,
    pub is_sensor: i32,
}

/// Структура для представления информации о контакте
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct ContactInfoFFI {
    pub block_id_a: i32,
    pub block_id_b: i32,
    pub point: Vector2FFI,
    pub normal: Vector2FFI,
    pub penetration: f32,
}

/// Типы блоков Tetris
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum BlockType {
    IBlock = 0,
    JBlock = 1,
    LBlock = 2,
    OBlock = 3,
    SBlock = 4,
    TBlock = 5,
    ZBlock = 6,
    Custom = 7,
}

/// Типы материалов
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MaterialType {
    Normal = 0,
    Heavy = 1,
    Light = 2,
    Bouncy = 3,
    Ice = 4,
    Sticky = 5,
    Custom = 6,
}

impl PhysicsManager {
    /// Создает новый экземпляр менеджера физики
    pub fn new(config: &PhysicsConfig) -> Result<Self> {
        Ok(Self {
            config: config.clone(),
            library: Arc::new(RwLock::new(None)),
            engine_ptr: Arc::new(RwLock::new(None)),
            running: Arc::new(RwLock::new(false)),
        })
    }
    
    /// Запускает менеджер физики
    pub async fn start(&self) -> Result<()> {
        let mut running = self.running.write().await;
        if *running {
            return Ok(());
        }
        *running = true;

        let mut lib_guard = self.library.write().await;
        if lib_guard.is_none() {
            let lib = unsafe { Library::new(&self.config.library_path)? };
            *lib_guard = Some(lib);
        }

        let lib_guard = self.library.read().await;
        let lib = lib_guard.as_ref().unwrap();

        let mut engine_guard = self.engine_ptr.write().await;
        if engine_guard.is_none() {
            let init_engine: Symbol<unsafe extern "C" fn() -> *mut c_void> = unsafe { lib.get(b"init_physics_engine")? };
            *engine_guard = Some(unsafe { init_engine() });
        }

        Ok(())
    }
    
    /// Останавливает менеджер физики
    pub async fn stop(&self) -> Result<()> {
        let mut running = self.running.write().await;
        if !*running {
            return Ok(());
        }

        let engine_guard = self.engine_ptr.read().await;
        if let Some(engine_ptr) = *engine_guard {
            let lib_guard = self.library.read().await;
            if let Some(lib) = &*lib_guard {
                let cleanup_engine: Symbol<unsafe extern "C" fn(*mut c_void)> = unsafe { lib.get(b"cleanup_physics_engine")? };
                unsafe { cleanup_engine(engine_ptr) };
            }
        }

        let mut engine_guard = self.engine_ptr.write().await;
        *engine_guard = None;

        let mut lib_guard = self.library.write().await;
        *lib_guard = None;

        *running = false;
        Ok(())
    }
    
    /// Проверяет, работает ли менеджер физики
    pub async fn is_running(&self) -> bool {
        *self.running.read().await
    }
    
    /// Создает блок с указанными параметрами
    pub async fn create_block(
        &self,
        position: (f32, f32),
        size: (f32, f32),
        angle: f32,
        material: Option<PhysicsMaterialFFI>,
        is_static: bool,
    ) -> Result<i32> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let create_block: Symbol<unsafe extern "C" fn(*mut c_void, Vector2FFI, Vector2FFI, f32, PhysicsMaterialFFI, i32) -> i32> = unsafe {
            library.get(b"physics_engine_create_block").context("Failed to get physics_engine_create_block function")?
        };
        
        let position_ffi = Vector2FFI {
            x: position.0,
            y: position.1,
        };
        
        let size_ffi = Vector2FFI {
            x: size.0,
            y: size.1,
        };
        
        let material_ffi = material.unwrap_or(PhysicsMaterialFFI {
            density: 1.0,
            restitution: 0.1,
            friction: 0.3,
            is_sensor: 0,
        });
        
        let block_id = unsafe {
            create_block(engine_ptr, position_ffi, size_ffi, angle, material_ffi, if is_static { 1 } else { 0 })
        };
        
        if block_id < 0 {
            return Err(anyhow::anyhow!("Failed to create block"));
        }
        
        Ok(block_id)
    }
    
    /// Создает блок Tetris указанного типа
    pub async fn create_tetris_block(
        &self,
        block_type: BlockType,
        position: (f32, f32),
        block_size: f32,
        angle: f32,
        material: Option<PhysicsMaterialFFI>,
    ) -> Result<Vec<i32>> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let create_tetris_block: Symbol<unsafe extern "C" fn(*mut c_void, i32, Vector2FFI, f32, f32, PhysicsMaterialFFI, *mut i32) -> *mut i32> = unsafe {
            library.get(b"physics_engine_create_tetris_block").context("Failed to get physics_engine_create_tetris_block function")?
        };
        
        let position_ffi = Vector2FFI {
            x: position.0,
            y: position.1,
        };
        
        let material_ffi = material.unwrap_or(PhysicsMaterialFFI {
            density: 1.0,
            restitution: 0.1,
            friction: 0.3,
            is_sensor: 0,
        });
        
        let mut count: i32 = 0;
        let block_ids_ptr = unsafe {
            create_tetris_block(engine_ptr, block_type as i32, position_ffi, block_size, angle, material_ffi, &mut count)
        };
        
        if block_ids_ptr.is_null() || count <= 0 {
            return Err(anyhow::anyhow!("Failed to create tetris block"));
        }
        
        let block_ids = unsafe {
            std::slice::from_raw_parts(block_ids_ptr, count as usize).to_vec()
        };
        
        // Освобождаем память, выделенную в C++
        let free_int_array: Symbol<unsafe extern "C" fn(*mut i32)> = unsafe {
            library.get(b"physics_free_int_array").context("Failed to get physics_free_int_array function")?
        };
        
        unsafe {
            free_int_array(block_ids_ptr);
        }
        
        Ok(block_ids)
    }
    
    /// Удаляет блок с указанным ID
    pub async fn remove_block(&self, block_id: i32) -> Result<bool> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let remove_block: Symbol<unsafe extern "C" fn(*mut c_void, i32) -> i32> = unsafe {
            library.get(b"physics_engine_remove_block").context("Failed to get physics_engine_remove_block function")?
        };
        
        let result = unsafe {
            remove_block(engine_ptr, block_id)
        };
        
        Ok(result != 0)
    }
    
    /// Проверяет коллизию между двумя блоками
    pub async fn check_collision(&self, block_id_a: i32, block_id_b: i32) -> Result<bool> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let check_collision: Symbol<unsafe extern "C" fn(*mut c_void, i32, i32) -> i32> = unsafe {
            library.get(b"physics_engine_check_collision").context("Failed to get physics_engine_check_collision function")?
        };
        
        let result = unsafe {
            check_collision(engine_ptr, block_id_a, block_id_b)
        };
        
        Ok(result != 0)
    }
    
    /// Применяет взрыв в указанной точке
    pub async fn apply_explosion(&self, center: (f32, f32), radius: f32, force: f32) -> Result<()> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let apply_explosion: Symbol<unsafe extern "C" fn(*mut c_void, Vector2FFI, f32, f32)> = unsafe {
            library.get(b"physics_engine_apply_explosion").context("Failed to get physics_engine_apply_explosion function")?
        };
        
        let center_ffi = Vector2FFI {
            x: center.0,
            y: center.1,
        };
        
        unsafe {
            apply_explosion(engine_ptr, center_ffi, radius, force);
        }
        
        Ok(())
    }
    
    /// Применяет ветер в указанном направлении
    pub async fn apply_wind(&self, direction: (f32, f32), strength: f32) -> Result<()> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let apply_wind: Symbol<unsafe extern "C" fn(*mut c_void, Vector2FFI, f32)> = unsafe {
            library.get(b"physics_engine_apply_wind").context("Failed to get physics_engine_apply_wind function")?
        };
        
        let direction_ffi = Vector2FFI {
            x: direction.0,
            y: direction.1,
        };
        
        unsafe {
            apply_wind(engine_ptr, direction_ffi, strength);
        }
        
        Ok(())
    }
    
    /// Получает позицию блока
    pub async fn get_block_position(&self, block_id: i32) -> Result<(f32, f32)> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let get_position: Symbol<unsafe extern "C" fn(*mut c_void, i32) -> Vector2FFI> = unsafe {
            library.get(b"physics_block_get_position").context("Failed to get physics_block_get_position function")?
        };
        
        let position = unsafe {
            get_position(engine_ptr, block_id)
        };
        
        Ok((position.x, position.y))
    }
    
    /// Устанавливает позицию блока
    pub async fn set_block_position(&self, block_id: i32, position: (f32, f32)) -> Result<()> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let set_position: Symbol<unsafe extern "C" fn(*mut c_void, i32, Vector2FFI)> = unsafe {
            library.get(b"physics_block_set_position").context("Failed to get physics_block_set_position function")?
        };
        
        let position_ffi = Vector2FFI {
            x: position.0,
            y: position.1,
        };
        
        unsafe {
            set_position(engine_ptr, block_id, position_ffi);
        }
        
        Ok(())
    }
    
    /// Получает угол блока
    pub async fn get_block_angle(&self, block_id: i32) -> Result<f32> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let get_angle: Symbol<unsafe extern "C" fn(*mut c_void, i32) -> f32> = unsafe {
            library.get(b"physics_block_get_angle").context("Failed to get physics_block_get_angle function")?
        };
        
        let angle = unsafe {
            get_angle(engine_ptr, block_id)
        };
        
        Ok(angle)
    }
    
    /// Устанавливает угол блока
    pub async fn set_block_angle(&self, block_id: i32, angle: f32) -> Result<()> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let set_angle: Symbol<unsafe extern "C" fn(*mut c_void, i32, f32)> = unsafe {
            library.get(b"physics_block_set_angle").context("Failed to get physics_block_set_angle function")?
        };
        
        unsafe {
            set_angle(engine_ptr, block_id, angle);
        }
        
        Ok(())
    }
    
    /// Сериализует состояние физического движка в JSON
    pub async fn serialize_to_json(&self) -> Result<String> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let serialize_to_json: Symbol<unsafe extern "C" fn(*mut c_void) -> *const c_char> = unsafe {
            library.get(b"physics_engine_serialize_to_json").context("Failed to get physics_engine_serialize_to_json function")?
        };
        
        let json_ptr = unsafe {
            serialize_to_json(engine_ptr)
        };
        
        if json_ptr.is_null() {
            return Err(anyhow::anyhow!("Failed to serialize physics engine state"));
        }
        
        let json = unsafe {
            std::ffi::CStr::from_ptr(json_ptr).to_string_lossy().into_owned()
        };
        
        // Освобождаем память, выделенную в C++
        let free_string: Symbol<unsafe extern "C" fn(*const c_char)> = unsafe {
            library.get(b"physics_free_string").context("Failed to get physics_free_string function")?
        };
        
        unsafe {
            free_string(json_ptr);
        }
        
        Ok(json)
    }
    
    /// Десериализует состояние физического движка из JSON
    pub async fn deserialize_from_json(&self, json: &str) -> Result<bool> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let deserialize_from_json: Symbol<unsafe extern "C" fn(*mut c_void, *const c_char) -> i32> = unsafe {
            library.get(b"physics_engine_deserialize_from_json").context("Failed to get physics_engine_deserialize_from_json function")?
        };
        
        let json_cstring = CString::new(json).context("Failed to create CString from JSON")?;
        
        let result = unsafe {
            deserialize_from_json(engine_ptr, json_cstring.as_ptr())
        };
        
        Ok(result != 0)
    }
    
    /// Обновляет физический движок на один шаг
    pub async fn update(&self, delta_time: f32) -> Result<()> {
        let engine_guard = self.engine_ptr.read().await;
        let engine_ptr = engine_guard.context("Physics engine not initialized")?;
        
        let lib_guard = self.library.read().await;
        let library = lib_guard.as_ref().context("Physics library not loaded")?;
        
        let update: Symbol<unsafe extern "C" fn(*mut c_void, f32)> = unsafe {
            library.get(b"physics_engine_update").context("Failed to get physics_engine_update function")?
        };
        
        unsafe {
            update(engine_ptr, delta_time);
        }
        
        Ok(())
    }
}

impl Drop for PhysicsManager {
    fn drop(&mut self) {
        // Остановка менеджера при уничтожении
        if *self.running.blocking_read() {
            if let Err(e) = self.stop() {
                error!("Error stopping Physics Manager during drop: {}", e);
            }
        }
    }
}
