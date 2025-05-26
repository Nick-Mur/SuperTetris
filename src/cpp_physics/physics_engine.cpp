#include <iostream>
#include <vector>
#include <memory>
#include <box2d/box2d.h>

/**
 * PhysicsEngine - Ядро физического движка для игры Tetris с элементами Tricky Towers
 * Реализовано на C++ с использованием библиотеки Box2D для физической симуляции
 */
class PhysicsEngine {
public:
    // Структура для хранения состояния физического тела
    struct BodyState {
        int id;
        float x;
        float y;
        float angle;
        float width;
        float height;
        bool isStatic;
    };

    PhysicsEngine() : world(std::make_unique<b2World>(b2Vec2(0.0f, -10.0f))) {
        std::cout << "Physics Engine initialized with default gravity" << std::endl;
    }

    ~PhysicsEngine() {
        std::cout << "Physics Engine destroyed" << std::endl;
    }

    // Инициализация физического движка с заданными параметрами
    void initialize(float gravityX, float gravityY, float timeStep) {
        world = std::make_unique<b2World>(b2Vec2(gravityX, gravityY));
        this->timeStep = timeStep;
        std::cout << "Physics Engine initialized with gravity (" << gravityX << ", " << gravityY << ")" << std::endl;
    }

    // Создание физического тела с заданными параметрами
    int createBody(float x, float y, float width, float height, bool isStatic) {
        b2BodyDef bodyDef;
        bodyDef.position.Set(x, y);
        bodyDef.type = isStatic ? b2_staticBody : b2_dynamicBody;
        
        b2Body* body = world->CreateBody(&bodyDef);
        
        b2PolygonShape shape;
        shape.SetAsBox(width / 2.0f, height / 2.0f);
        
        b2FixtureDef fixtureDef;
        fixtureDef.shape = &shape;
        fixtureDef.density = isStatic ? 0.0f : 1.0f;
        fixtureDef.friction = 0.3f;
        fixtureDef.restitution = 0.1f; // Небольшой отскок
        
        body->CreateFixture(&fixtureDef);
        
        int id = nextBodyId++;
        bodies[id] = body;
        
        std::cout << "Created body with ID " << id << " at position (" << x << ", " << y << ")" << std::endl;
        
        return id;
    }

    // Применение силы к телу
    void applyForce(int bodyId, float forceX, float forceY) {
        auto it = bodies.find(bodyId);
        if (it != bodies.end()) {
            b2Body* body = it->second;
            body->ApplyForceToCenter(b2Vec2(forceX, forceY), true);
            std::cout << "Applied force (" << forceX << ", " << forceY << ") to body " << bodyId << std::endl;
        } else {
            std::cerr << "Body with ID " << bodyId << " not found" << std::endl;
        }
    }

    // Применение импульса к телу
    void applyImpulse(int bodyId, float impulseX, float impulseY) {
        auto it = bodies.find(bodyId);
        if (it != bodies.end()) {
            b2Body* body = it->second;
            body->ApplyLinearImpulseToCenter(b2Vec2(impulseX, impulseY), true);
            std::cout << "Applied impulse (" << impulseX << ", " << impulseY << ") to body " << bodyId << std::endl;
        } else {
            std::cerr << "Body with ID " << bodyId << " not found" << std::endl;
        }
    }

    // Установка линейной скорости тела
    void setLinearVelocity(int bodyId, float velocityX, float velocityY) {
        auto it = bodies.find(bodyId);
        if (it != bodies.end()) {
            b2Body* body = it->second;
            body->SetLinearVelocity(b2Vec2(velocityX, velocityY));
            std::cout << "Set linear velocity (" << velocityX << ", " << velocityY << ") to body " << bodyId << std::endl;
        } else {
            std::cerr << "Body with ID " << bodyId << " not found" << std::endl;
        }
    }

    // Установка угловой скорости тела
    void setAngularVelocity(int bodyId, float velocity) {
        auto it = bodies.find(bodyId);
        if (it != bodies.end()) {
            b2Body* body = it->second;
            body->SetAngularVelocity(velocity);
            std::cout << "Set angular velocity " << velocity << " to body " << bodyId << std::endl;
        } else {
            std::cerr << "Body with ID " << bodyId << " not found" << std::endl;
        }
    }

    // Выполнение шага физической симуляции
    void step() {
        const int velocityIterations = 8;
        const int positionIterations = 3;
        
        world->Step(timeStep, velocityIterations, positionIterations);
        std::cout << "Physics step performed" << std::endl;
    }

    // Получение состояния всех тел
    std::vector<BodyState> getBodyStates() {
        std::vector<BodyState> states;
        
        for (const auto& pair : bodies) {
            int id = pair.first;
            b2Body* body = pair.second;
            
            b2Vec2 position = body->GetPosition();
            float angle = body->GetAngle();
            
            // Получаем размеры тела из первой фикстуры (предполагаем, что это прямоугольник)
            float width = 1.0f;
            float height = 1.0f;
            
            b2Fixture* fixture = body->GetFixtureList();
            if (fixture) {
                b2Shape* shape = fixture->GetShape();
                if (shape->GetType() == b2Shape::e_polygon) {
                    b2PolygonShape* poly = (b2PolygonShape*)shape;
                    // Предполагаем, что это прямоугольник, созданный с помощью SetAsBox
                    width = poly->m_vertices[2].x - poly->m_vertices[0].x;
                    height = poly->m_vertices[2].y - poly->m_vertices[0].y;
                }
            }
            
            bool isStatic = body->GetType() == b2_staticBody;
            
            states.push_back({id, position.x, position.y, angle, width, height, isStatic});
        }
        
        return states;
    }

    // Удаление тела
    void destroyBody(int bodyId) {
        auto it = bodies.find(bodyId);
        if (it != bodies.end()) {
            world->DestroyBody(it->second);
            bodies.erase(it);
            std::cout << "Destroyed body with ID " << bodyId << std::endl;
        } else {
            std::cerr << "Body with ID " << bodyId << " not found" << std::endl;
        }
    }

    // Проверка столкновений между телами
    bool checkCollision(int bodyId1, int bodyId2) {
        auto it1 = bodies.find(bodyId1);
        auto it2 = bodies.find(bodyId2);
        
        if (it1 != bodies.end() && it2 != bodies.end()) {
            b2Body* body1 = it1->second;
            b2Body* body2 = it2->second;
            
            // Проверяем столкновение между всеми фикстурами тел
            for (b2Fixture* f1 = body1->GetFixtureList(); f1; f1 = f1->GetNext()) {
                for (b2Fixture* f2 = body2->GetFixtureList(); f2; f2 = f2->GetNext()) {
                    b2WorldManifold worldManifold;
                    if (f1->GetAABB(0).TestOverlap(f2->GetAABB(0))) {
                        return true;
                    }
                }
            }
        }
        
        return false;
    }

private:
    std::unique_ptr<b2World> world;
    std::unordered_map<int, b2Body*> bodies;
    int nextBodyId = 1;
    float timeStep = 1.0f / 60.0f;
};

// Функция для экспорта в Python через pybind11
extern "C" {
    PhysicsEngine* createPhysicsEngine() {
        return new PhysicsEngine();
    }
    
    void destroyPhysicsEngine(PhysicsEngine* engine) {
        delete engine;
    }
    
    void initializePhysicsEngine(PhysicsEngine* engine, float gravityX, float gravityY, float timeStep) {
        engine->initialize(gravityX, gravityY, timeStep);
    }
    
    int createBody(PhysicsEngine* engine, float x, float y, float width, float height, bool isStatic) {
        return engine->createBody(x, y, width, height, isStatic);
    }
    
    void applyForce(PhysicsEngine* engine, int bodyId, float forceX, float forceY) {
        engine->applyForce(bodyId, forceX, forceY);
    }
    
    void step(PhysicsEngine* engine) {
        engine->step();
    }
}

// Пример использования
int main() {
    PhysicsEngine engine;
    
    // Инициализация с гравитацией, направленной вниз
    engine.initialize(0.0f, -10.0f, 1.0f / 60.0f);
    
    // Создание статической платформы
    int platformId = engine.createBody(0.0f, -10.0f, 20.0f, 1.0f, true);
    
    // Создание динамического блока
    int blockId = engine.createBody(0.0f, 10.0f, 1.0f, 1.0f, false);
    
    // Симуляция падения блока на платформу
    for (int i = 0; i < 100; i++) {
        engine.step();
        
        // Получение состояния тел
        auto states = engine.getBodyStates();
        
        // Вывод позиции блока
        for (const auto& state : states) {
            if (state.id == blockId) {
                std::cout << "Block position: (" << state.x << ", " << state.y << ")" << std::endl;
            }
        }
    }
    
    return 0;
}
