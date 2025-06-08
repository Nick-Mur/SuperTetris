#include "include/PhysicsEngine.h"
#include <iostream>
#include <chrono>
#include <thread>
#include <cmath>

using namespace TetrisTowers;

// Функция обратного вызова для обработки коллизий
void onCollision(const ContactInfo& contact) {
    std::cout << "Collision detected between blocks " << contact.blockIdA 
              << " and " << contact.blockIdB << " at point (" 
              << contact.point.x << ", " << contact.point.y << ")" << std::endl;
}

int main() {
    std::cout << "Tetris Towers Physics Engine Example" << std::endl;
    std::cout << "===================================" << std::endl;
    
    // Создание физического движка с гравитацией, направленной вниз
    PhysicsEngine engine(Vector2(0, -9.8f));
    
    // Установка обратного вызова для обработки коллизий
    engine.setCollisionCallback(onCollision);
    
    // Создание пола (статический блок)
    int floorId = engine.createBlock(
        Vector2(0, -10),         // Позиция
        Vector2(20, 1),          // Размер
        0,                       // Угол
        PhysicsMaterial(1.0f, 0.3f, 0.5f),  // Материал
        true                     // Статический
    );
    
    std::cout << "Created floor with ID: " << floorId << std::endl;
    
    // Создание различных блоков Tetris
    std::vector<int> iBlockIds = engine.createTetrisBlock(
        BlockType::I_BLOCK,
        Vector2(0, 10),          // Позиция
        1.0f,                    // Размер блока
        0,                       // Угол
        PhysicsMaterial::createFromType(MaterialType::NORMAL)
    );
    
    std::cout << "Created I-block with IDs: ";
    for (int id : iBlockIds) {
        std::cout << id << " ";
    }
    std::cout << std::endl;
    
    std::vector<int> lBlockIds = engine.createTetrisBlock(
        BlockType::L_BLOCK,
        Vector2(5, 15),          // Позиция
        1.0f,                    // Размер блока
        M_PI / 4,                // Угол (45 градусов)
        PhysicsMaterial::createFromType(MaterialType::HEAVY)
    );
    
    std::cout << "Created L-block with IDs: ";
    for (int id : lBlockIds) {
        std::cout << id << " ";
    }
    std::cout << std::endl;
    
    std::vector<int> tBlockIds = engine.createTetrisBlock(
        BlockType::T_BLOCK,
        Vector2(-5, 12),         // Позиция
        1.0f,                    // Размер блока
        0,                       // Угол
        PhysicsMaterial::createFromType(MaterialType::BOUNCY)
    );
    
    std::cout << "Created T-block with IDs: ";
    for (int id : tBlockIds) {
        std::cout << id << " ";
    }
    std::cout << std::endl;
    
    // Запуск симуляции в отдельном потоке
    engine.startSimulation(1.0f / 60.0f);
    
    // Основной цикл симуляции
    const int simulationSteps = 300;  // 5 секунд при 60 FPS
    for (int step = 0; step < simulationSteps; ++step) {
        // Вывод позиций блоков каждые 60 шагов (примерно 1 секунда)
        if (step % 60 == 0) {
            std::cout << "\nSimulation time: " << step / 60.0f << " seconds" << std::endl;
            
            // Вывод позиции I-блока
            if (!iBlockIds.empty()) {
                PhysicsBlock* block = engine.getBlock(iBlockIds[0]);
                if (block) {
                    Vector2 pos = block->getPosition();
                    std::cout << "I-block position: (" << pos.x << ", " << pos.y << ")" << std::endl;
                }
            }
            
            // Вывод позиции L-блока
            if (!lBlockIds.empty()) {
                PhysicsBlock* block = engine.getBlock(lBlockIds[0]);
                if (block) {
                    Vector2 pos = block->getPosition();
                    std::cout << "L-block position: (" << pos.x << ", " << pos.y << ")" << std::endl;
                }
            }
            
            // Вывод позиции T-блока
            if (!tBlockIds.empty()) {
                PhysicsBlock* block = engine.getBlock(tBlockIds[0]);
                if (block) {
                    Vector2 pos = block->getPosition();
                    std::cout << "T-block position: (" << pos.x << ", " << pos.y << ")" << std::endl;
                }
            }
        }
        
        // Добавление случайных сил и импульсов для демонстрации
        if (step == 120) {  // После 2 секунд
            std::cout << "\nApplying explosion at (0, 0) with radius 10 and force 50" << std::endl;
            engine.applyExplosion(Vector2(0, 0), 10, 50);
        }
        
        if (step == 180) {  // После 3 секунд
            std::cout << "\nApplying wind from left to right with strength 5" << std::endl;
            engine.applyWind(Vector2(1, 0), 5);
        }
        
        // Пауза для синхронизации с реальным временем
        std::this_thread::sleep_for(std::chrono::milliseconds(16));  // ~60 FPS
    }
    
    // Остановка симуляции
    engine.stopSimulation();
    
    std::cout << "\nSimulation completed" << std::endl;
    
    // Сериализация состояния физического движка в JSON
    std::string json = engine.serializeToJson();
    std::cout << "\nFinal state of the physics engine:\n" << json << std::endl;
    
    return 0;
}
