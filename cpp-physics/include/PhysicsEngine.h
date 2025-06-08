#ifndef PHYSICS_ENGINE_H
#define PHYSICS_ENGINE_H

#include <vector>
#include <memory>
#include <string>
#include <functional>
#include <unordered_map>
#include <mutex>
#include <thread>
#include <chrono>
#include <cmath>

namespace TetrisTowers {

// Типы тетромино
enum class TetrominoType {
    I, J, L, O, S, T, Z
};

// Типы материалов
enum class MaterialType {
    NORMAL,     // Обычный блок
    HEAVY,      // Тяжелый блок (увеличенная масса)
    LIGHT,      // Легкий блок (уменьшенная масса)
    SLIPPERY,   // Скользкий блок (уменьшенное трение)
    STICKY,     // Липкий блок (увеличенное трение)
    BOUNCY      // Упругий блок (увеличенная упругость)
};

// Структура для представления 2D вектора
struct Vector2 {
    float x;
    float y;
    
    Vector2() : x(0.0f), y(0.0f) {}
    Vector2(float x, float y) : x(x), y(y) {}
    
    Vector2 operator+(const Vector2& other) const {
        return Vector2(x + other.x, y + other.y);
    }
    
    Vector2 operator-(const Vector2& other) const {
        return Vector2(x - other.x, y - other.y);
    }
    
    Vector2 operator*(float scalar) const {
        return Vector2(x * scalar, y * scalar);
    }
    
    float length() const {
        return std::sqrt(x * x + y * y);
    }
    
    Vector2 normalized() const {
        float len = length();
        if (len > 0) {
            return Vector2(x / len, y / len);
        }
        return *this;
    }
    
    float dot(const Vector2& other) const {
        return x * other.x + y * other.y;
    }
};

// Структура для представления физического тела
struct PhysicsBody {
    std::string id;           // Уникальный идентификатор
    Vector2 position;         // Позиция центра тела
    Vector2 velocity;         // Скорость
    Vector2 force;            // Сила, действующая на тело
    float rotation;           // Угол поворота в радианах
    float angularVelocity;    // Угловая скорость
    float torque;             // Крутящий момент
    float mass;               // Масса
    float inverseMass;        // Обратная масса (1/mass)
    float inertia;            // Момент инерции
    float inverseInertia;     // Обратный момент инерции
    float restitution;        // Коэффициент упругости (0-1)
    float friction;           // Коэффициент трения (0-1)
    bool isStatic;            // Статическое тело (не двигается)
    bool isActive;            // Активно ли тело
    MaterialType material;    // Тип материала
    
    // Форма тела (для простоты используем только прямоугольники)
    float width;
    float height;
    
    PhysicsBody() : 
        id(""), position(), velocity(), force(), rotation(0.0f), 
        angularVelocity(0.0f), torque(0.0f), mass(1.0f), inverseMass(1.0f),
        inertia(0.0f), inverseInertia(0.0f), restitution(0.5f), friction(0.3f),
        isStatic(false), isActive(true), material(MaterialType::NORMAL),
        width(1.0f), height(1.0f) {
        
        updateMassData();
    }
    
    // Обновление данных о массе и инерции
    void updateMassData() {
        if (isStatic) {
            inverseMass = 0.0f;
            inverseInertia = 0.0f;
            return;
        }
        
        inverseMass = 1.0f / mass;
        
        // Момент инерции для прямоугольника
        inertia = mass * (width * width + height * height) / 12.0f;
        inverseInertia = 1.0f / inertia;
    }
    
    // Применение силы к телу
    void applyForce(const Vector2& f) {
        force = force + f;
    }
    
    // Применение импульса к телу
    void applyImpulse(const Vector2& impulse, const Vector2& contactPoint) {
        velocity = velocity + impulse * inverseMass;
        
        // Вычисление плеча силы
        Vector2 r = contactPoint - position;
        
        // Вычисление крутящего момента (2D cross product)
        float cross = r.x * impulse.y - r.y * impulse.x;
        
        // Применение углового импульса
        angularVelocity += cross * inverseInertia;
    }
    
    // Получение скорости в заданной точке тела
    Vector2 getVelocityAtPoint(const Vector2& point) const {
        Vector2 r = point - position;
        Vector2 tangent(-r.y, r.x);  // Перпендикулярный вектор
        return velocity + tangent * angularVelocity;
    }
    
    // Проверка, находится ли точка внутри тела
    bool containsPoint(const Vector2& point) const {
        // Преобразование точки в локальные координаты тела
        float cosA = std::cos(-rotation);
        float sinA = std::sin(-rotation);
        
        Vector2 localPoint;
        localPoint.x = cosA * (point.x - position.x) - sinA * (point.y - position.y);
        localPoint.y = sinA * (point.x - position.x) + cosA * (point.y - position.y);
        
        // Проверка, находится ли точка внутри прямоугольника
        return (localPoint.x >= -width/2 && localPoint.x <= width/2 &&
                localPoint.y >= -height/2 && localPoint.y <= height/2);
    }
    
    // Получение вершин прямоугольника в мировых координатах
    std::vector<Vector2> getVertices() const {
        std::vector<Vector2> vertices(4);
        
        float cosA = std::cos(rotation);
        float sinA = std::sin(rotation);
        
        // Локальные координаты вершин
        Vector2 halfSize(width/2, height/2);
        Vector2 v1(-halfSize.x, -halfSize.y);
        Vector2 v2(halfSize.x, -halfSize.y);
        Vector2 v3(halfSize.x, halfSize.y);
        Vector2 v4(-halfSize.x, halfSize.y);
        
        // Преобразование в мировые координаты
        vertices[0].x = position.x + cosA * v1.x - sinA * v1.y;
        vertices[0].y = position.y + sinA * v1.x + cosA * v1.y;
        
        vertices[1].x = position.x + cosA * v2.x - sinA * v2.y;
        vertices[1].y = position.y + sinA * v2.x + cosA * v2.y;
        
        vertices[2].x = position.x + cosA * v3.x - sinA * v3.y;
        vertices[2].y = position.y + sinA * v3.x + cosA * v3.y;
        
        vertices[3].x = position.x + cosA * v4.x - sinA * v4.y;
        vertices[3].y = position.y + sinA * v4.x + cosA * v4.y;
        
        return vertices;
    }
};

// Структура для представления контакта между телами
struct Contact {
    PhysicsBody* bodyA;
    PhysicsBody* bodyB;
    Vector2 point;        // Точка контакта
    Vector2 normal;       // Нормаль контакта (от A к B)
    float penetration;    // Глубина проникновения
    
    Contact() : bodyA(nullptr), bodyB(nullptr), point(), normal(), penetration(0.0f) {}
};

// Структура для представления тетромино
struct Tetromino {
    TetrominoType type;
    std::vector<PhysicsBody> blocks;
    
    Tetromino() : type(TetrominoType::I) {}
    Tetromino(TetrominoType type) : type(type) {}
};

// Класс физического движка
class PhysicsEngine {
public:
    PhysicsEngine();
    ~PhysicsEngine();
    
    // Инициализация движка
    bool initialize();
    
    // Завершение работы движка
    void shutdown();
    
    // Обновление физики
    void update(float deltaTime);
    
    // Создание нового тела
    std::string createBody(const PhysicsBody& body);
    
    // Получение тела по ID
    PhysicsBody* getBody(const std::string& id);
    
    // Удаление тела
    bool removeBody(const std::string& id);
    
    // Создание тетромино заданного типа
    Tetromino createTetromino(TetrominoType type, const Vector2& position, float rotation = 0.0f);
    
    // Применение силы к телу
    void applyForce(const std::string& bodyId, const Vector2& force);
    
    // Применение импульса к телу
    void applyImpulse(const std::string& bodyId, const Vector2& impulse, const Vector2& contactPoint);
    
    // Установка гравитации
    void setGravity(const Vector2& gravity);
    
    // Получение текущей гравитации
    Vector2 getGravity() const;
    
    // Проверка стабильности башни
    bool checkTowerStability(const std::vector<std::string>& towerBlockIds);
    
    // Регистрация колбэка для обработки коллизий
    void registerCollisionCallback(std::function<void(const Contact&)> callback);
    
    // Запуск/остановка симуляции
    void startSimulation();
    void pauseSimulation();
    void stopSimulation();
    
    // Получение всех тел
    std::vector<PhysicsBody*> getAllBodies();
    
    // Проверка пересечения двух тел
    bool checkCollision(const PhysicsBody& bodyA, const PhysicsBody& bodyB, Contact* contact = nullptr);
    
    // Проверка, находится ли точка внутри тела
    bool isPointInBody(const std::string& bodyId, const Vector2& point);
    
    // Получение тел в заданной области
    std::vector<PhysicsBody*> getBodiesInArea(const Vector2& min, const Vector2& max);
    
    // Применение заклинания (изменение физических свойств блоков)
    void applySpell(const std::string& spellType, const std::vector<std::string>& targetBlockIds);
    
    // Экспорт состояния физики в JSON
    std::string exportStateToJson();
    
    // Импорт состояния физики из JSON
    bool importStateFromJson(const std::string& json);
    
private:
    // Внутренние методы
    
    // Обнаружение коллизий
    void detectCollisions();
    
    // Разрешение коллизий
    void resolveCollisions();
    
    // Интеграция физики
    void integrate(float deltaTime);
    
    // Генерация уникального ID
    std::string generateUniqueId();
    
    // Проверка пересечения двух прямоугольников (AABB)
    bool checkAABBCollision(const PhysicsBody& bodyA, const PhysicsBody& bodyB);
    
    // Проверка пересечения двух ориентированных прямоугольников (OBB)
    bool checkOBBCollision(const PhysicsBody& bodyA, const PhysicsBody& bodyB, Contact* contact);
    
    // Разделяющая ось для OBB
    bool checkSeparatingAxis(const std::vector<Vector2>& verticesA, 
                            const std::vector<Vector2>& verticesB, 
                            const Vector2& axis, 
                            float& minOverlap,
                            Vector2& normal);
    
    // Поток симуляции
    void simulationThread();
    
private:
    // Данные движка
    std::unordered_map<std::string, PhysicsBody> m_bodies;
    std::vector<Contact> m_contacts;
    Vector2 m_gravity;
    
    // Колбэк для обработки коллизий
    std::function<void(const Contact&)> m_collisionCallback;
    
    // Параметры симуляции
    float m_timeStep;
    int m_velocityIterations;
    int m_positionIterations;
    
    // Управление потоком симуляции
    std::thread m_simulationThread;
    std::mutex m_mutex;
    bool m_isRunning;
    bool m_isPaused;
};

} // namespace TetrisTowers

#endif // PHYSICS_ENGINE_H
