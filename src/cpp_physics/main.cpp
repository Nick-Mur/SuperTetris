#include "include/PhysicsEngine.h"
#include <iostream>
#include <chrono>
#include <thread>
#include <iomanip>

using namespace TetrisTowers;

// Функция для вывода информации о теле
void printBodyInfo(const PhysicsBody* body) {
    if (!body) {
        std::cout << "Body not found!" << std::endl;
        return;
    }
    
    std::cout << "Body ID: " << body->id << std::endl;
    std::cout << "Position: (" << body->position.x << ", " << body->position.y << ")" << std::endl;
    std::cout << "Velocity: (" << body->velocity.x << ", " << body->velocity.y << ")" << std::endl;
    std::cout << "Rotation: " << body->rotation << " rad" << std::endl;
    std::cout << "Angular Velocity: " << body->angularVelocity << " rad/s" << std::endl;
    std::cout << "Mass: " << body->mass << std::endl;
    std::cout << "Is Static: " << (body->isStatic ? "Yes" : "No") << std::endl;
    std::cout << "Material: " << static_cast<int>(body->material) << std::endl;
    std::cout << "Size: " << body->width << " x " << body->height << std::endl;
    std::cout << std::endl;
}

// Функция для вывода информации о тетромино
void printTetrominoInfo(const Tetromino& tetromino) {
    std::cout << "Tetromino Type: ";
    switch (tetromino.type) {
        case TetrominoType::I: std::cout << "I"; break;
        case TetrominoType::J: std::cout << "J"; break;
        case TetrominoType::L: std::cout << "L"; break;
        case TetrominoType::O: std::cout << "O"; break;
        case TetrominoType::S: std::cout << "S"; break;
        case TetrominoType::T: std::cout << "T"; break;
        case TetrominoType::Z: std::cout << "Z"; break;
    }
    std::cout << std::endl;
    
    std::cout << "Number of Blocks: " << tetromino.blocks.size() << std::endl;
    
    for (size_t i = 0; i < tetromino.blocks.size(); ++i) {
        std::cout << "Block " << i << ":" << std::endl;
        std::cout << "  Position: (" << tetromino.blocks[i].position.x << ", " 
                  << tetromino.blocks[i].position.y << ")" << std::endl;
        std::cout << "  Rotation: " << tetromino.blocks[i].rotation << " rad" << std::endl;
    }
    
    std::cout << std::endl;
}

// Колбэк для обработки коллизий
void onCollision(const Contact& contact) {
    std::cout << "Collision detected between bodies: " << contact.bodyA->id << " and " << contact.bodyB->id << std::endl;
    std::cout << "Contact point: (" << contact.point.x << ", " << contact.point.y << ")" << std::endl;
    std::cout << "Normal: (" << contact.normal.x << ", " << contact.normal.y << ")" << std::endl;
    std::cout << "Penetration: " << contact.penetration << std::endl;
    std::cout << std::endl;
}

// Тест создания и удаления тел
void testBodyCreationAndRemoval() {
    std::cout << "=== Test Body Creation and Removal ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Создание тела
    PhysicsBody body;
    body.position = Vector2(1.0f, 2.0f);
    body.rotation = 0.5f;
    body.width = 2.0f;
    body.height = 1.0f;
    
    std::string id = engine.createBody(body);
    std::cout << "Created body with ID: " << id << std::endl;
    
    // Получение тела
    PhysicsBody* retrievedBody = engine.getBody(id);
    std::cout << "Retrieved body:" << std::endl;
    printBodyInfo(retrievedBody);
    
    // Удаление тела
    bool removed = engine.removeBody(id);
    std::cout << "Body removed: " << (removed ? "Yes" : "No") << std::endl;
    
    // Попытка получить удаленное тело
    retrievedBody = engine.getBody(id);
    std::cout << "Retrieved body after removal: " << (retrievedBody ? "Found" : "Not found") << std::endl;
    
    std::cout << std::endl;
}

// Тест создания тетромино
void testTetrominoCreation() {
    std::cout << "=== Test Tetromino Creation ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Создание тетромино разных типов
    std::vector<TetrominoType> types = {
        TetrominoType::I, TetrominoType::J, TetrominoType::L, 
        TetrominoType::O, TetrominoType::S, TetrominoType::T, TetrominoType::Z
    };
    
    for (auto type : types) {
        Tetromino tetromino = engine.createTetromino(type, Vector2(0.0f, 0.0f));
        printTetrominoInfo(tetromino);
        
        // Добавление блоков тетромино в движок
        for (auto& block : tetromino.blocks) {
            engine.createBody(block);
        }
    }
    
    std::cout << std::endl;
}

// Тест применения сил и импульсов
void testForcesAndImpulses() {
    std::cout << "=== Test Forces and Impulses ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Создание тела
    PhysicsBody body;
    body.position = Vector2(0.0f, 0.0f);
    body.mass = 1.0f;
    
    std::string id = engine.createBody(body);
    std::cout << "Initial state:" << std::endl;
    printBodyInfo(engine.getBody(id));
    
    // Применение силы
    engine.applyForce(id, Vector2(10.0f, 5.0f));
    std::cout << "After applying force:" << std::endl;
    
    // Обновление физики
    engine.update(0.1f);
    printBodyInfo(engine.getBody(id));
    
    // Применение импульса
    engine.applyImpulse(id, Vector2(0.0f, 20.0f), Vector2(0.0f, 0.0f));
    std::cout << "After applying impulse:" << std::endl;
    
    // Обновление физики
    engine.update(0.1f);
    printBodyInfo(engine.getBody(id));
    
    std::cout << std::endl;
}

// Тест обнаружения коллизий
void testCollisionDetection() {
    std::cout << "=== Test Collision Detection ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Регистрация колбэка для коллизий
    engine.registerCollisionCallback(onCollision);
    
    // Создание двух пересекающихся тел
    PhysicsBody bodyA;
    bodyA.position = Vector2(0.0f, 0.0f);
    bodyA.width = 2.0f;
    bodyA.height = 2.0f;
    
    PhysicsBody bodyB;
    bodyB.position = Vector2(1.0f, 1.0f);
    bodyB.width = 2.0f;
    bodyB.height = 2.0f;
    
    std::string idA = engine.createBody(bodyA);
    std::string idB = engine.createBody(bodyB);
    
    std::cout << "Body A:" << std::endl;
    printBodyInfo(engine.getBody(idA));
    
    std::cout << "Body B:" << std::endl;
    printBodyInfo(engine.getBody(idB));
    
    // Проверка коллизии
    Contact contact;
    bool colliding = engine.checkCollision(*engine.getBody(idA), *engine.getBody(idB), &contact);
    
    std::cout << "Bodies are colliding: " << (colliding ? "Yes" : "No") << std::endl;
    if (colliding) {
        std::cout << "Contact information:" << std::endl;
        std::cout << "Point: (" << contact.point.x << ", " << contact.point.y << ")" << std::endl;
        std::cout << "Normal: (" << contact.normal.x << ", " << contact.normal.y << ")" << std::endl;
        std::cout << "Penetration: " << contact.penetration << std::endl;
    }
    
    // Обновление физики для обработки коллизий
    engine.update(0.1f);
    
    std::cout << std::endl;
}

// Тест стабильности башни
void testTowerStability() {
    std::cout << "=== Test Tower Stability ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Создание башни из блоков
    std::vector<std::string> towerBlockIds;
    
    // Основание башни (статическое)
    PhysicsBody base;
    base.position = Vector2(0.0f, 0.0f);
    base.width = 3.0f;
    base.height = 1.0f;
    base.isStatic = true;
    
    std::string baseId = engine.createBody(base);
    towerBlockIds.push_back(baseId);
    
    // Блоки башни
    for (int i = 1; i <= 5; ++i) {
        PhysicsBody block;
        block.position = Vector2(0.0f, i * 1.0f);
        block.width = 1.0f;
        block.height = 1.0f;
        
        std::string blockId = engine.createBody(block);
        towerBlockIds.push_back(blockId);
    }
    
    // Проверка стабильности башни
    bool isStable = engine.checkTowerStability(towerBlockIds);
    std::cout << "Tower is stable: " << (isStable ? "Yes" : "No") << std::endl;
    
    // Смещение верхнего блока для нарушения стабильности
    PhysicsBody* topBlock = engine.getBody(towerBlockIds.back());
    if (topBlock) {
        topBlock->position.x = 2.0f;
        
        // Повторная проверка стабильности
        isStable = engine.checkTowerStability(towerBlockIds);
        std::cout << "Tower is stable after moving top block: " << (isStable ? "Yes" : "No") << std::endl;
    }
    
    std::cout << std::endl;
}

// Тест применения заклинаний
void testSpells() {
    std::cout << "=== Test Spells ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Создание блока
    PhysicsBody block;
    block.position = Vector2(0.0f, 0.0f);
    block.mass = 1.0f;
    block.friction = 0.3f;
    block.restitution = 0.5f;
    
    std::string blockId = engine.createBody(block);
    std::cout << "Initial block state:" << std::endl;
    printBodyInfo(engine.getBody(blockId));
    
    // Применение различных заклинаний
    std::vector<std::string> spells = {
        "heavy", "light", "slippery", "sticky", "bouncy", "normal"
    };
    
    for (const auto& spell : spells) {
        std::cout << "Applying spell: " << spell << std::endl;
        engine.applySpell(spell, {blockId});
        std::cout << "Block state after spell:" << std::endl;
        printBodyInfo(engine.getBody(blockId));
    }
    
    std::cout << std::endl;
}

// Тест симуляции падения блоков
void testFallingBlocks() {
    std::cout << "=== Test Falling Blocks ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Установка гравитации
    engine.setGravity(Vector2(0.0f, -9.8f));
    
    // Создание земли (статическое тело)
    PhysicsBody ground;
    ground.position = Vector2(0.0f, -5.0f);
    ground.width = 20.0f;
    ground.height = 1.0f;
    ground.isStatic = true;
    
    std::string groundId = engine.createBody(ground);
    
    // Создание падающего блока
    PhysicsBody fallingBlock;
    fallingBlock.position = Vector2(0.0f, 10.0f);
    fallingBlock.width = 1.0f;
    fallingBlock.height = 1.0f;
    fallingBlock.mass = 1.0f;
    
    std::string blockId = engine.createBody(fallingBlock);
    
    std::cout << "Initial block position: (" << engine.getBody(blockId)->position.x 
              << ", " << engine.getBody(blockId)->position.y << ")" << std::endl;
    
    // Симуляция падения
    const int numSteps = 10;
    const float timeStep = 0.1f;
    
    for (int i = 0; i < numSteps; ++i) {
        engine.update(timeStep);
        
        PhysicsBody* block = engine.getBody(blockId);
        if (block) {
            std::cout << "Step " << i + 1 << ": Position = (" 
                      << block->position.x << ", " << block->position.y 
                      << "), Velocity = (" << block->velocity.x << ", " << block->velocity.y << ")" << std::endl;
        }
    }
    
    std::cout << std::endl;
}

// Тест экспорта состояния в JSON
void testStateExport() {
    std::cout << "=== Test State Export ===" << std::endl;
    
    PhysicsEngine engine;
    engine.initialize();
    
    // Создание нескольких тел
    PhysicsBody bodyA;
    bodyA.position = Vector2(1.0f, 2.0f);
    bodyA.rotation = 0.5f;
    
    PhysicsBody bodyB;
    bodyB.position = Vector2(-1.0f, -2.0f);
    bodyB.rotation = -0.5f;
    bodyB.isStatic = true;
    
    engine.createBody(bodyA);
    engine.createBody(bodyB);
    
    // Экспорт состояния
    std::string json = engine.exportStateToJson();
    std::cout << "Exported state:" << std::endl;
    std::cout << json << std::endl;
    
    std::cout << std::endl;
}

// Основная функция для тестирования физического движка
int main() {
    std::cout << "=== Physics Engine Test ===" << std::endl;
    std::cout << std::endl;
    
    // Запуск тестов
    testBodyCreationAndRemoval();
    testTetrominoCreation();
    testForcesAndImpulses();
    testCollisionDetection();
    testTowerStability();
    testSpells();
    testFallingBlocks();
    testStateExport();
    
    std::cout << "All tests completed!" << std::endl;
    
    return 0;
}
