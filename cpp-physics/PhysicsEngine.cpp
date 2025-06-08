#include "include/PhysicsEngine.h"
#include <algorithm>
#include <random>
#include <sstream>
#include <iomanip>
#include <chrono>

namespace TetrisTowers {

// Конструктор
PhysicsEngine::PhysicsEngine() 
    : m_gravity(0.0f, -9.8f), 
      m_timeStep(1.0f/60.0f),
      m_velocityIterations(8),
      m_positionIterations(3),
      m_isRunning(false),
      m_isPaused(false) {
}

// Деструктор
PhysicsEngine::~PhysicsEngine() {
    shutdown();
}

// Инициализация движка
bool PhysicsEngine::initialize() {
    m_bodies.clear();
    m_contacts.clear();
    m_gravity = Vector2(0.0f, -9.8f);
    m_isRunning = false;
    m_isPaused = false;
    return true;
}

// Завершение работы движка
void PhysicsEngine::shutdown() {
    stopSimulation();
    m_bodies.clear();
    m_contacts.clear();
}

// Обновление физики
void PhysicsEngine::update(float deltaTime) {
    if (m_isPaused) return;
    
    std::lock_guard<std::mutex> lock(m_mutex);
    
    // Обнаружение коллизий
    detectCollisions();
    
    // Разрешение коллизий
    resolveCollisions();
    
    // Интеграция физики
    integrate(deltaTime);
}

// Создание нового тела
std::string PhysicsEngine::createBody(const PhysicsBody& body) {
    std::string id = generateUniqueId();
    PhysicsBody newBody = body;
    newBody.id = id;
    
    std::lock_guard<std::mutex> lock(m_mutex);
    m_bodies[id] = newBody;
    return id;
}

// Получение тела по ID
PhysicsBody* PhysicsEngine::getBody(const std::string& id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    auto it = m_bodies.find(id);
    if (it != m_bodies.end()) {
        return &it->second;
    }
    return nullptr;
}

// Удаление тела
bool PhysicsEngine::removeBody(const std::string& id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    auto it = m_bodies.find(id);
    if (it != m_bodies.end()) {
        m_bodies.erase(it);
        return true;
    }
    return false;
}

// Создание тетромино заданного типа
Tetromino PhysicsEngine::createTetromino(TetrominoType type, const Vector2& position, float rotation) {
    Tetromino tetromino(type);
    
    // Размер блока
    const float blockSize = 1.0f;
    
    // Определение формы тетромино в зависимости от типа
    std::vector<Vector2> blockPositions;
    
    switch (type) {
        case TetrominoType::I:
            // I-тетромино (4 блока в линию)
            blockPositions = {
                Vector2(-1.5f * blockSize, 0.0f),
                Vector2(-0.5f * blockSize, 0.0f),
                Vector2(0.5f * blockSize, 0.0f),
                Vector2(1.5f * blockSize, 0.0f)
            };
            break;
            
        case TetrominoType::J:
            // J-тетромино
            blockPositions = {
                Vector2(-1.0f * blockSize, 0.5f * blockSize),
                Vector2(-1.0f * blockSize, -0.5f * blockSize),
                Vector2(0.0f * blockSize, -0.5f * blockSize),
                Vector2(1.0f * blockSize, -0.5f * blockSize)
            };
            break;
            
        case TetrominoType::L:
            // L-тетромино
            blockPositions = {
                Vector2(-1.0f * blockSize, -0.5f * blockSize),
                Vector2(0.0f * blockSize, -0.5f * blockSize),
                Vector2(1.0f * blockSize, -0.5f * blockSize),
                Vector2(1.0f * blockSize, 0.5f * blockSize)
            };
            break;
            
        case TetrominoType::O:
            // O-тетромино (квадрат)
            blockPositions = {
                Vector2(-0.5f * blockSize, -0.5f * blockSize),
                Vector2(-0.5f * blockSize, 0.5f * blockSize),
                Vector2(0.5f * blockSize, -0.5f * blockSize),
                Vector2(0.5f * blockSize, 0.5f * blockSize)
            };
            break;
            
        case TetrominoType::S:
            // S-тетромино
            blockPositions = {
                Vector2(-1.0f * blockSize, -0.5f * blockSize),
                Vector2(0.0f * blockSize, -0.5f * blockSize),
                Vector2(0.0f * blockSize, 0.5f * blockSize),
                Vector2(1.0f * blockSize, 0.5f * blockSize)
            };
            break;
            
        case TetrominoType::T:
            // T-тетромино
            blockPositions = {
                Vector2(-1.0f * blockSize, -0.5f * blockSize),
                Vector2(0.0f * blockSize, -0.5f * blockSize),
                Vector2(1.0f * blockSize, -0.5f * blockSize),
                Vector2(0.0f * blockSize, 0.5f * blockSize)
            };
            break;
            
        case TetrominoType::Z:
            // Z-тетромино
            blockPositions = {
                Vector2(-1.0f * blockSize, 0.5f * blockSize),
                Vector2(0.0f * blockSize, 0.5f * blockSize),
                Vector2(0.0f * blockSize, -0.5f * blockSize),
                Vector2(1.0f * blockSize, -0.5f * blockSize)
            };
            break;
    }
    
    // Создание блоков тетромино
    for (const auto& blockPos : blockPositions) {
        PhysicsBody block;
        
        // Поворот позиции блока
        float cosA = std::cos(rotation);
        float sinA = std::sin(rotation);
        Vector2 rotatedPos;
        rotatedPos.x = cosA * blockPos.x - sinA * blockPos.y;
        rotatedPos.y = sinA * blockPos.x + cosA * blockPos.y;
        
        // Установка параметров блока
        block.position = position + rotatedPos;
        block.rotation = rotation;
        block.width = blockSize;
        block.height = blockSize;
        block.mass = 1.0f;
        block.restitution = 0.1f;
        block.friction = 0.8f;
        block.material = MaterialType::NORMAL;
        block.updateMassData();
        
        // Добавление блока в тетромино
        tetromino.blocks.push_back(block);
    }
    
    return tetromino;
}

// Применение силы к телу
void PhysicsEngine::applyForce(const std::string& bodyId, const Vector2& force) {
    std::lock_guard<std::mutex> lock(m_mutex);
    auto it = m_bodies.find(bodyId);
    if (it != m_bodies.end()) {
        it->second.applyForce(force);
    }
}

// Применение импульса к телу
void PhysicsEngine::applyImpulse(const std::string& bodyId, const Vector2& impulse, const Vector2& contactPoint) {
    std::lock_guard<std::mutex> lock(m_mutex);
    auto it = m_bodies.find(bodyId);
    if (it != m_bodies.end()) {
        it->second.applyImpulse(impulse, contactPoint);
    }
}

// Установка гравитации
void PhysicsEngine::setGravity(const Vector2& gravity) {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_gravity = gravity;
}

// Получение текущей гравитации
Vector2 PhysicsEngine::getGravity() const {
    return m_gravity;
}

// Проверка стабильности башни
bool PhysicsEngine::checkTowerStability(const std::vector<std::string>& towerBlockIds) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    // Если башня пустая, считаем её стабильной
    if (towerBlockIds.empty()) {
        return true;
    }
    
    // Проверяем, что все блоки существуют
    std::vector<PhysicsBody*> towerBlocks;
    for (const auto& id : towerBlockIds) {
        auto it = m_bodies.find(id);
        if (it != m_bodies.end()) {
            towerBlocks.push_back(&it->second);
        } else {
            // Если какой-то блок не найден, считаем башню нестабильной
            return false;
        }
    }
    
    // Проверка стабильности по скорости блоков
    const float velocityThreshold = 0.1f;
    const float angularVelocityThreshold = 0.1f;
    
    for (const auto& block : towerBlocks) {
        if (block->velocity.length() > velocityThreshold || 
            std::abs(block->angularVelocity) > angularVelocityThreshold) {
            return false;
        }
    }
    
    // Проверка стабильности по положению центра масс
    // Находим самый нижний блок
    PhysicsBody* lowestBlock = nullptr;
    float lowestY = std::numeric_limits<float>::max();
    
    for (const auto& block : towerBlocks) {
        if (block->position.y < lowestY) {
            lowestY = block->position.y;
            lowestBlock = block;
        }
    }
    
    if (!lowestBlock) {
        return false;
    }
    
    // Вычисляем центр масс башни
    Vector2 centerOfMass(0.0f, 0.0f);
    float totalMass = 0.0f;
    
    for (const auto& block : towerBlocks) {
        centerOfMass = centerOfMass + block->position * block->mass;
        totalMass += block->mass;
    }
    
    if (totalMass > 0.0f) {
        centerOfMass = centerOfMass * (1.0f / totalMass);
    }
    
    // Проверяем, что центр масс находится над основанием нижнего блока
    float baseLeft = lowestBlock->position.x - lowestBlock->width / 2.0f;
    float baseRight = lowestBlock->position.x + lowestBlock->width / 2.0f;
    
    return (centerOfMass.x >= baseLeft && centerOfMass.x <= baseRight);
}

// Регистрация колбэка для обработки коллизий
void PhysicsEngine::registerCollisionCallback(std::function<void(const Contact&)> callback) {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_collisionCallback = callback;
}

// Запуск симуляции
void PhysicsEngine::startSimulation() {
    if (m_isRunning) {
        return;
    }
    
    m_isRunning = true;
    m_isPaused = false;
    
    // Запуск потока симуляции
    m_simulationThread = std::thread(&PhysicsEngine::simulationThread, this);
}

// Пауза симуляции
void PhysicsEngine::pauseSimulation() {
    m_isPaused = true;
}

// Остановка симуляции
void PhysicsEngine::stopSimulation() {
    if (!m_isRunning) {
        return;
    }
    
    m_isRunning = false;
    
    // Ожидание завершения потока симуляции
    if (m_simulationThread.joinable()) {
        m_simulationThread.join();
    }
}

// Получение всех тел
std::vector<PhysicsBody*> PhysicsEngine::getAllBodies() {
    std::lock_guard<std::mutex> lock(m_mutex);
    std::vector<PhysicsBody*> bodies;
    bodies.reserve(m_bodies.size());
    
    for (auto& pair : m_bodies) {
        bodies.push_back(&pair.second);
    }
    
    return bodies;
}

// Проверка пересечения двух тел
bool PhysicsEngine::checkCollision(const PhysicsBody& bodyA, const PhysicsBody& bodyB, Contact* contact) {
    // Сначала проверяем AABB для быстрого отсечения
    if (!checkAABBCollision(bodyA, bodyB)) {
        return false;
    }
    
    // Затем проверяем OBB для точного определения коллизии
    return checkOBBCollision(bodyA, bodyB, contact);
}

// Проверка, находится ли точка внутри тела
bool PhysicsEngine::isPointInBody(const std::string& bodyId, const Vector2& point) {
    std::lock_guard<std::mutex> lock(m_mutex);
    auto it = m_bodies.find(bodyId);
    if (it != m_bodies.end()) {
        return it->second.containsPoint(point);
    }
    return false;
}

// Получение тел в заданной области
std::vector<PhysicsBody*> PhysicsEngine::getBodiesInArea(const Vector2& min, const Vector2& max) {
    std::lock_guard<std::mutex> lock(m_mutex);
    std::vector<PhysicsBody*> result;
    
    for (auto& pair : m_bodies) {
        PhysicsBody& body = pair.second;
        
        // Проверяем, находится ли тело в заданной области
        // Для простоты используем AABB тела
        float halfWidth = body.width / 2.0f;
        float halfHeight = body.height / 2.0f;
        
        // Вычисляем AABB тела
        float bodyMinX = body.position.x - halfWidth;
        float bodyMaxX = body.position.x + halfWidth;
        float bodyMinY = body.position.y - halfHeight;
        float bodyMaxY = body.position.y + halfHeight;
        
        // Проверяем пересечение AABB тела с заданной областью
        if (bodyMaxX >= min.x && bodyMinX <= max.x &&
            bodyMaxY >= min.y && bodyMinY <= max.y) {
            result.push_back(&body);
        }
    }
    
    return result;
}

// Применение заклинания (изменение физических свойств блоков)
void PhysicsEngine::applySpell(const std::string& spellType, const std::vector<std::string>& targetBlockIds) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    // Применяем заклинание к каждому блоку
    for (const auto& id : targetBlockIds) {
        auto it = m_bodies.find(id);
        if (it != m_bodies.end()) {
            PhysicsBody& body = it->second;
            
            if (spellType == "heavy") {
                // Увеличиваем массу блока
                body.mass *= 2.0f;
                body.material = MaterialType::HEAVY;
                body.updateMassData();
            }
            else if (spellType == "light") {
                // Уменьшаем массу блока
                body.mass *= 0.5f;
                body.material = MaterialType::LIGHT;
                body.updateMassData();
            }
            else if (spellType == "slippery") {
                // Уменьшаем трение
                body.friction *= 0.2f;
                body.material = MaterialType::SLIPPERY;
            }
            else if (spellType == "sticky") {
                // Увеличиваем трение
                body.friction *= 2.0f;
                body.material = MaterialType::STICKY;
            }
            else if (spellType == "bouncy") {
                // Увеличиваем упругость
                body.restitution = 0.9f;
                body.material = MaterialType::BOUNCY;
            }
            else if (spellType == "normal") {
                // Возвращаем нормальные свойства
                body.mass = 1.0f;
                body.friction = 0.3f;
                body.restitution = 0.5f;
                body.material = MaterialType::NORMAL;
                body.updateMassData();
            }
            else if (spellType == "impulse_up") {
                // Применяем импульс вверх
                body.applyImpulse(Vector2(0.0f, 10.0f), body.position);
            }
            else if (spellType == "impulse_down") {
                // Применяем импульс вниз
                body.applyImpulse(Vector2(0.0f, -5.0f), body.position);
            }
            else if (spellType == "impulse_left") {
                // Применяем импульс влево
                body.applyImpulse(Vector2(-5.0f, 0.0f), body.position);
            }
            else if (spellType == "impulse_right") {
                // Применяем импульс вправо
                body.applyImpulse(Vector2(5.0f, 0.0f), body.position);
            }
            else if (spellType == "rotate_cw") {
                // Применяем вращение по часовой стрелке
                body.angularVelocity += 2.0f;
            }
            else if (spellType == "rotate_ccw") {
                // Применяем вращение против часовой стрелки
                body.angularVelocity -= 2.0f;
            }
        }
    }
}

// Экспорт состояния физики в JSON
std::string PhysicsEngine::exportStateToJson() {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    std::stringstream ss;
    ss << "{\n";
    
    // Экспорт гравитации
    ss << "  \"gravity\": {\"x\": " << m_gravity.x << ", \"y\": " << m_gravity.y << "},\n";
    
    // Экспорт тел
    ss << "  \"bodies\": [\n";
    
    bool firstBody = true;
    for (const auto& pair : m_bodies) {
        const PhysicsBody& body = pair.second;
        
        if (!firstBody) {
            ss << ",\n";
        }
        firstBody = false;
        
        ss << "    {\n";
        ss << "      \"id\": \"" << body.id << "\",\n";
        ss << "      \"position\": {\"x\": " << body.position.x << ", \"y\": " << body.position.y << "},\n";
        ss << "      \"velocity\": {\"x\": " << body.velocity.x << ", \"y\": " << body.velocity.y << "},\n";
        ss << "      \"rotation\": " << body.rotation << ",\n";
        ss << "      \"angularVelocity\": " << body.angularVelocity << ",\n";
        ss << "      \"width\": " << body.width << ",\n";
        ss << "      \"height\": " << body.height << ",\n";
        ss << "      \"mass\": " << body.mass << ",\n";
        ss << "      \"restitution\": " << body.restitution << ",\n";
        ss << "      \"friction\": " << body.friction << ",\n";
        ss << "      \"isStatic\": " << (body.isStatic ? "true" : "false") << ",\n";
        ss << "      \"material\": " << static_cast<int>(body.material) << "\n";
        ss << "    }";
    }
    
    ss << "\n  ]\n";
    ss << "}\n";
    
    return ss.str();
}

// Импорт состояния физики из JSON
bool PhysicsEngine::importStateFromJson(const std::string& json) {
    // Примечание: для полноценной реализации требуется библиотека для работы с JSON
    // В данном примере мы просто возвращаем false, чтобы показать, что функция не реализована
    return false;
}

// Внутренние методы

// Обнаружение коллизий
void PhysicsEngine::detectCollisions() {
    m_contacts.clear();
    
    // Проверяем все пары тел на коллизии
    std::vector<PhysicsBody*> bodies = getAllBodies();
    
    for (size_t i = 0; i < bodies.size(); ++i) {
        for (size_t j = i + 1; j < bodies.size(); ++j) {
            Contact contact;
            if (checkCollision(*bodies[i], *bodies[j], &contact)) {
                m_contacts.push_back(contact);
                
                // Вызываем колбэк, если он зарегистрирован
                if (m_collisionCallback) {
                    m_collisionCallback(contact);
                }
            }
        }
    }
}

// Разрешение коллизий
void PhysicsEngine::resolveCollisions() {
    for (auto& contact : m_contacts) {
        PhysicsBody* bodyA = contact.bodyA;
        PhysicsBody* bodyB = contact.bodyB;
        
        // Если оба тела статические, пропускаем
        if (bodyA->isStatic && bodyB->isStatic) {
            continue;
        }
        
        // Относительная скорость в точке контакта
        Vector2 relativeVelocity = bodyB->getVelocityAtPoint(contact.point) - 
                                  bodyA->getVelocityAtPoint(contact.point);
        
        // Скорость вдоль нормали
        float velocityAlongNormal = relativeVelocity.dot(contact.normal);
        
        // Если тела разлетаются, пропускаем
        if (velocityAlongNormal > 0) {
            continue;
        }
        
        // Вычисление коэффициента восстановления (среднее значение)
        float restitution = std::min(bodyA->restitution, bodyB->restitution);
        
        // Вычисление импульса
        float j = -(1.0f + restitution) * velocityAlongNormal;
        j /= bodyA->inverseMass + bodyB->inverseMass;
        
        // Применение импульса
        Vector2 impulse = contact.normal * j;
        
        if (!bodyA->isStatic) {
            bodyA->applyImpulse(impulse * -1.0f, contact.point);
        }
        
        if (!bodyB->isStatic) {
            bodyB->applyImpulse(impulse, contact.point);
        }
        
        // Трение
        // Вычисление тангенциальной составляющей
        Vector2 tangent = relativeVelocity - contact.normal * velocityAlongNormal;
        float tangentLength = tangent.length();
        
        if (tangentLength > 0.0001f) {
            tangent = tangent * (1.0f / tangentLength);
            
            // Вычисление силы трения
            float jt = -relativeVelocity.dot(tangent);
            jt /= bodyA->inverseMass + bodyB->inverseMass;
            
            // Коэффициент трения (среднее значение)
            float friction = (bodyA->friction + bodyB->friction) * 0.5f;
            
            // Ограничение силы трения
            float maxJt = j * friction;
            jt = std::max(-maxJt, std::min(jt, maxJt));
            
            // Применение силы трения
            Vector2 frictionImpulse = tangent * jt;
            
            if (!bodyA->isStatic) {
                bodyA->applyImpulse(frictionImpulse * -1.0f, contact.point);
            }
            
            if (!bodyB->isStatic) {
                bodyB->applyImpulse(frictionImpulse, contact.point);
            }
        }
        
        // Коррекция позиций для предотвращения проникновения
        const float percent = 0.2f; // Обычно 20-80%
        const float slop = 0.01f; // Небольшое значение для предотвращения дрожания
        
        Vector2 correction = contact.normal * (std::max(contact.penetration - slop, 0.0f) * percent);
        correction = correction * (bodyA->inverseMass + bodyB->inverseMass);
        
        if (!bodyA->isStatic) {
            bodyA->position = bodyA->position - correction * bodyA->inverseMass;
        }
        
        if (!bodyB->isStatic) {
            bodyB->position = bodyB->position + correction * bodyB->inverseMass;
        }
    }
}

// Интеграция физики
void PhysicsEngine::integrate(float deltaTime) {
    for (auto& pair : m_bodies) {
        PhysicsBody& body = pair.second;
        
        // Пропускаем статические тела
        if (body.isStatic || !body.isActive) {
            continue;
        }
        
        // Применяем гравитацию
        body.applyForce(m_gravity * body.mass);
        
        // Интегрирование скорости
        body.velocity = body.velocity + body.force * body.inverseMass * deltaTime;
        body.angularVelocity += body.torque * body.inverseInertia * deltaTime;
        
        // Затухание скорости
        const float linearDamping = 0.98f;
        const float angularDamping = 0.98f;
        
        body.velocity = body.velocity * linearDamping;
        body.angularVelocity *= angularDamping;
        
        // Интегрирование позиции
        body.position = body.position + body.velocity * deltaTime;
        body.rotation += body.angularVelocity * deltaTime;
        
        // Сброс сил и моментов
        body.force = Vector2(0.0f, 0.0f);
        body.torque = 0.0f;
    }
}

// Генерация уникального ID
std::string PhysicsEngine::generateUniqueId() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<> dis(0, 15);
    static const char* digits = "0123456789abcdef";
    
    std::stringstream ss;
    ss << "body_";
    
    for (int i = 0; i < 8; ++i) {
        ss << digits[dis(gen)];
    }
    
    return ss.str();
}

// Проверка пересечения двух прямоугольников (AABB)
bool PhysicsEngine::checkAABBCollision(const PhysicsBody& bodyA, const PhysicsBody& bodyB) {
    // Вычисляем AABB для каждого тела
    float halfWidthA = bodyA.width / 2.0f;
    float halfHeightA = bodyA.height / 2.0f;
    float halfWidthB = bodyB.width / 2.0f;
    float halfHeightB = bodyB.height / 2.0f;
    
    // Вычисляем границы AABB
    float minAx = bodyA.position.x - halfWidthA;
    float maxAx = bodyA.position.x + halfWidthA;
    float minAy = bodyA.position.y - halfHeightA;
    float maxAy = bodyA.position.y + halfHeightA;
    
    float minBx = bodyB.position.x - halfWidthB;
    float maxBx = bodyB.position.x + halfWidthB;
    float minBy = bodyB.position.y - halfHeightB;
    float maxBy = bodyB.position.y + halfHeightB;
    
    // Проверяем пересечение AABB
    return (maxAx >= minBx && minAx <= maxBx && maxAy >= minBy && minAy <= maxBy);
}

// Проверка пересечения двух ориентированных прямоугольников (OBB)
bool PhysicsEngine::checkOBBCollision(const PhysicsBody& bodyA, const PhysicsBody& bodyB, Contact* contact) {
    // Получаем вершины прямоугольников
    std::vector<Vector2> verticesA = bodyA.getVertices();
    std::vector<Vector2> verticesB = bodyB.getVertices();
    
    // Оси для проверки (нормали к сторонам прямоугольников)
    std::vector<Vector2> axes;
    
    // Добавляем оси для первого прямоугольника
    for (size_t i = 0; i < verticesA.size(); ++i) {
        Vector2 edge = verticesA[(i + 1) % verticesA.size()] - verticesA[i];
        Vector2 normal(-edge.y, edge.x); // Перпендикуляр к ребру
        axes.push_back(normal.normalized());
    }
    
    // Добавляем оси для второго прямоугольника
    for (size_t i = 0; i < verticesB.size(); ++i) {
        Vector2 edge = verticesB[(i + 1) % verticesB.size()] - verticesB[i];
        Vector2 normal(-edge.y, edge.x); // Перпендикуляр к ребру
        axes.push_back(normal.normalized());
    }
    
    // Проверяем разделение по каждой оси
    float minOverlap = std::numeric_limits<float>::max();
    Vector2 minAxis;
    
    for (const auto& axis : axes) {
        float overlap = 0.0f;
        Vector2 normal;
        
        if (!checkSeparatingAxis(verticesA, verticesB, axis, overlap, normal)) {
            // Если найдена разделяющая ось, тела не пересекаются
            return false;
        }
        
        // Запоминаем минимальное перекрытие
        if (overlap < minOverlap) {
            minOverlap = overlap;
            minAxis = normal;
        }
    }
    
    // Если мы дошли до этой точки, значит тела пересекаются
    if (contact) {
        contact->bodyA = const_cast<PhysicsBody*>(&bodyA);
        contact->bodyB = const_cast<PhysicsBody*>(&bodyB);
        contact->normal = minAxis;
        contact->penetration = minOverlap;
        
        // Вычисление точки контакта (упрощенно - средняя точка пересечения)
        Vector2 centerA = bodyA.position;
        Vector2 centerB = bodyB.position;
        
        // Направление от A к B
        Vector2 direction = centerB - centerA;
        
        // Если направление совпадает с нормалью, используем его
        if (direction.dot(minAxis) < 0) {
            contact->normal = minAxis * -1.0f;
        }
        
        // Вычисляем точку контакта (упрощенно)
        contact->point = centerA + direction * 0.5f;
    }
    
    return true;
}

// Разделяющая ось для OBB
bool PhysicsEngine::checkSeparatingAxis(const std::vector<Vector2>& verticesA, 
                                       const std::vector<Vector2>& verticesB, 
                                       const Vector2& axis, 
                                       float& minOverlap,
                                       Vector2& normal) {
    // Проекции вершин на ось
    float minA = std::numeric_limits<float>::max();
    float maxA = -std::numeric_limits<float>::max();
    float minB = std::numeric_limits<float>::max();
    float maxB = -std::numeric_limits<float>::max();
    
    // Проецируем вершины первого тела
    for (const auto& vertex : verticesA) {
        float projection = vertex.dot(axis);
        minA = std::min(minA, projection);
        maxA = std::max(maxA, projection);
    }
    
    // Проецируем вершины второго тела
    for (const auto& vertex : verticesB) {
        float projection = vertex.dot(axis);
        minB = std::min(minB, projection);
        maxB = std::max(maxB, projection);
    }
    
    // Проверяем перекрытие проекций
    float overlap = std::min(maxA, maxB) - std::max(minA, minB);
    
    if (overlap < 0) {
        // Разделяющая ось найдена
        return false;
    }
    
    // Запоминаем перекрытие и нормаль
    minOverlap = overlap;
    normal = axis;
    
    // Определяем направление нормали
    if (minA < minB) {
        normal = normal * -1.0f;
    }
    
    return true;
}

// Поток симуляции
void PhysicsEngine::simulationThread() {
    auto lastTime = std::chrono::high_resolution_clock::now();
    
    while (m_isRunning) {
        auto currentTime = std::chrono::high_resolution_clock::now();
        float deltaTime = std::chrono::duration<float>(currentTime - lastTime).count();
        lastTime = currentTime;
        
        // Ограничиваем deltaTime для стабильности симуляции
        if (deltaTime > 0.05f) {
            deltaTime = 0.05f;
        }
        
        // Обновление физики
        update(deltaTime);
        
        // Пауза для снижения нагрузки на CPU
        std::this_thread::sleep_for(std::chrono::milliseconds(16)); // ~60 FPS
    }
}

} // namespace TetrisTowers
