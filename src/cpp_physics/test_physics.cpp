#include "include/PhysicsEngine.h"
#include <iostream>
#include <cassert>
#include <vector>
#include <cmath>
#include <chrono>
#include <thread>

using namespace TetrisTowers;

// Вспомогательная функция для проверки приблизительного равенства с плавающей точкой
bool approxEqual(float a, float b, float epsilon = 0.0001f) {
    return std::abs(a - b) < epsilon;
}

// Вспомогательная функция для проверки приблизительного равенства векторов
bool approxEqual(const Vector2& a, const Vector2& b, float epsilon = 0.0001f) {
    return approxEqual(a.x, b.x, epsilon) && approxEqual(a.y, b.y, epsilon);
}

// Тест для Vector2
void testVector2() {
    std::cout << "Testing Vector2..." << std::endl;
    
    // Тест конструкторов
    Vector2 v1;
    assert(v1.x == 0.0f && v1.y == 0.0f);
    
    Vector2 v2(3.0f, 4.0f);
    assert(v2.x == 3.0f && v2.y == 4.0f);
    
    // Тест операторов
    Vector2 v3 = v2 + Vector2(1.0f, 2.0f);
    assert(v3.x == 4.0f && v3.y == 6.0f);
    
    Vector2 v4 = v3 - v2;
    assert(v4.x == 1.0f && v4.y == 2.0f);
    
    Vector2 v5 = v2 * 2.0f;
    assert(v5.x == 6.0f && v5.y == 8.0f);
    
    // Тест методов
    float length = v2.length();
    assert(approxEqual(length, 5.0f));
    
    Vector2 normalized = v2.normalized();
    assert(approxEqual(normalized.x, 0.6f) && approxEqual(normalized.y, 0.8f));
    
    float dot = v2.dot(Vector2(2.0f, 1.0f));
    assert(approxEqual(dot, 10.0f));
    
    std::cout << "Vector2 tests passed!" << std::endl;
}

// Тест для PhysicsMaterial
void testPhysicsMaterial() {
    std::cout << "Testing PhysicsMaterial..." << std::endl;
    
    // Тест конструкторов
    PhysicsMaterial defaultMaterial;
    assert(defaultMaterial.density == 1.0f);
    assert(defaultMaterial.restitution == 0.1f);
    assert(defaultMaterial.friction == 0.3f);
    assert(!defaultMaterial.isSensor);
    
    PhysicsMaterial customMaterial(2.0f, 0.5f, 0.7f, true);
    assert(customMaterial.density == 2.0f);
    assert(customMaterial.restitution == 0.5f);
    assert(customMaterial.friction == 0.7f);
    assert(customMaterial.isSensor);
    
    // Тест создания из типа
    PhysicsMaterial normalMaterial = PhysicsMaterial::createFromType(MaterialType::NORMAL);
    assert(normalMaterial.density == 1.0f);
    assert(normalMaterial.restitution == 0.1f);
    assert(normalMaterial.friction == 0.3f);
    
    PhysicsMaterial bouncyMaterial = PhysicsMaterial::createFromType(MaterialType::BOUNCY);
    assert(bouncyMaterial.restitution > normalMaterial.restitution);
    
    PhysicsMaterial iceMaterial = PhysicsMaterial::createFromType(MaterialType::ICE);
    assert(iceMaterial.friction < normalMaterial.friction);
    
    std::cout << "PhysicsMaterial tests passed!" << std::endl;
}

// Тест для PhysicsBlock
void testPhysicsBlock() {
    std::cout << "Testing PhysicsBlock..." << std::endl;
    
    // Создание блока
    int id = 1;
    Vector2 position(3.0f, 4.0f);
    Vector2 size(2.0f, 2.0f);
    float angle = 0.0f;
    PhysicsMaterial material(1.0f, 0.5f, 0.3f);
    
    PhysicsBlock block(id, position, size, angle, material);
    
    // Проверка начальных значений
    assert(block.getId() == id);
    assert(approxEqual(block.getPosition(), position));
    assert(approxEqual(block.getSize(), size));
    assert(approxEqual(block.getAngle(), angle));
    assert(approxEqual(block.getLinearVelocity(), Vector2(0, 0)));
    assert(approxEqual(block.getAngularVelocity(), 0.0f));
    assert(!block.isStatic());
    
    // Тест установки позиции
    Vector2 newPosition(5.0f, 6.0f);
    block.setPosition(newPosition);
    assert(approxEqual(block.getPosition(), newPosition));
    
    // Тест установки угла
    float newAngle = 1.0f;
    block.setAngle(newAngle);
    assert(approxEqual(block.getAngle(), newAngle));
    
    // Тест установки скорости
    Vector2 newVelocity(2.0f, 3.0f);
    block.setLinearVelocity(newVelocity);
    assert(approxEqual(block.getLinearVelocity(), newVelocity));
    
    float newAngularVelocity = 0.5f;
    block.setAngularVelocity(newAngularVelocity);
    assert(approxEqual(block.getAngularVelocity(), newAngularVelocity));
    
    // Тест применения силы
    Vector2 force(10.0f, 20.0f);
    Vector2 expectedVelocity = newVelocity + force * (1.0f / block.getMass());
    block.applyForce(force);
    assert(approxEqual(block.getLinearVelocity(), expectedVelocity));
    
    // Тест обновления
    float deltaTime = 0.1f;
    Vector2 expectedPosition = newPosition + expectedVelocity * deltaTime;
    float expectedAngle = newAngle + newAngularVelocity * deltaTime;
    block.update(deltaTime);
    assert(approxEqual(block.getPosition(), expectedPosition));
    assert(approxEqual(block.getAngle(), expectedAngle));
    
    // Тест статического блока
    block.setStatic(true);
    assert(block.isStatic());
    assert(approxEqual(block.getLinearVelocity(), Vector2(0, 0)));
    assert(approxEqual(block.getAngularVelocity(), 0.0f));
    
    // Статический блок не должен изменять позицию при применении силы
    Vector2 positionBeforeForce = block.getPosition();
    block.applyForce(force);
    block.update(deltaTime);
    assert(approxEqual(block.getPosition(), positionBeforeForce));
    
    std::cout << "PhysicsBlock tests passed!" << std::endl;
}

// Тест для PhysicsEngine
void testPhysicsEngine() {
    std::cout << "Testing PhysicsEngine..." << std::endl;
    
    // Создание движка
    PhysicsEngine engine(Vector2(0, -9.8f));
    
    // Проверка начальных значений
    assert(approxEqual(engine.getGravity(), Vector2(0, -9.8f)));
    assert(engine.getIterations() == 10);
    
    // Тест создания блока
    int blockId = engine.createBlock(Vector2(0, 0), Vector2(1, 1));
    assert(blockId >= 0);
    
    PhysicsBlock* block = engine.getBlock(blockId);
    assert(block != nullptr);
    assert(block->getId() == blockId);
    
    // Тест создания блока Tetris
    std::vector<int> tetrisBlockIds = engine.createTetrisBlock(BlockType::I_BLOCK, Vector2(0, 5));
    assert(tetrisBlockIds.size() == 4);  // I-блок состоит из 4 квадратов
    
    for (int id : tetrisBlockIds) {
        PhysicsBlock* tetrisBlock = engine.getBlock(id);
        assert(tetrisBlock != nullptr);
    }
    
    // Тест удаления блока
    bool removed = engine.removeBlock(blockId);
    assert(removed);
    assert(engine.getBlock(blockId) == nullptr);
    
    // Тест обновления
    float deltaTime = 0.1f;
    engine.update(deltaTime);
    
    // Проверка применения гравитации
    for (int id : tetrisBlockIds) {
        PhysicsBlock* tetrisBlock = engine.getBlock(id);
        assert(tetrisBlock != nullptr);
        assert(tetrisBlock->getLinearVelocity().y < 0);  // Скорость должна быть направлена вниз
    }
    
    // Тест коллизии
    int floor = engine.createBlock(Vector2(0, -10), Vector2(20, 1), 0, PhysicsMaterial(), true);
    assert(floor >= 0);
    
    // Запуск симуляции на короткое время для проверки коллизии
    engine.startSimulation(1.0f / 60.0f);
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    engine.stopSimulation();
    
    // Проверка, что блоки остановились на полу
    for (int id : tetrisBlockIds) {
        PhysicsBlock* tetrisBlock = engine.getBlock(id);
        assert(tetrisBlock != nullptr);
        // Блоки должны быть выше пола
        assert(tetrisBlock->getPosition().y > -10);
    }
    
    std::cout << "PhysicsEngine tests passed!" << std::endl;
}

// Тест для проверки сериализации
void testSerialization() {
    std::cout << "Testing serialization..." << std::endl;
    
    PhysicsEngine engine;
    
    // Создание нескольких блоков
    int block1 = engine.createBlock(Vector2(1, 2), Vector2(3, 4), 0.5f);
    int block2 = engine.createBlock(Vector2(-1, -2), Vector2(2, 2), 0, PhysicsMaterial(), true);
    
    // Сериализация в JSON
    std::string json = engine.serializeToJson();
    
    // Проверка, что JSON содержит информацию о блоках
    assert(json.find("\"id\": " + std::to_string(block1)) != std::string::npos);
    assert(json.find("\"id\": " + std::to_string(block2)) != std::string::npos);
    
    std::cout << "Serialization tests passed!" << std::endl;
}

// Тест для проверки производительности
void testPerformance() {
    std::cout << "Testing performance..." << std::endl;
    
    PhysicsEngine engine;
    
    // Создание большого количества блоков
    const int numBlocks = 100;
    std::vector<int> blockIds;
    
    for (int i = 0; i < numBlocks; ++i) {
        float x = static_cast<float>(rand() % 20 - 10);
        float y = static_cast<float>(rand() % 20 + 10);
        int blockId = engine.createBlock(Vector2(x, y), Vector2(1, 1));
        blockIds.push_back(blockId);
    }
    
    // Создание пола
    int floor = engine.createBlock(Vector2(0, -10), Vector2(30, 1), 0, PhysicsMaterial(), true);
    
    // Измерение времени выполнения обновления
    auto start = std::chrono::high_resolution_clock::now();
    
    const int numUpdates = 100;
    for (int i = 0; i < numUpdates; ++i) {
        engine.update(1.0f / 60.0f);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    
    std::cout << "Performed " << numUpdates << " updates with " << numBlocks 
              << " blocks in " << elapsed.count() << " seconds" << std::endl;
    std::cout << "Average time per update: " << elapsed.count() / numUpdates 
              << " seconds" << std::endl;
    
    std::cout << "Performance tests passed!" << std::endl;
}

int main() {
    std::cout << "Running physics engine tests..." << std::endl;
    
    // Запуск тестов
    testVector2();
    testPhysicsMaterial();
    testPhysicsBlock();
    testPhysicsEngine();
    testSerialization();
    testPerformance();
    
    std::cout << "All tests passed!" << std::endl;
    return 0;
}
