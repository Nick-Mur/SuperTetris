# Интеграция компонентов и межъязыковое взаимодействие

В этом документе описывается архитектура интеграции различных компонентов игры Tetris с элементами Tricky Towers, реализованных на разных языках программирования.

## Общая схема взаимодействия

```
+-------------------+     +-------------------+     +-------------------+
| Клиентская часть  |     |  Серверная часть  |     |  Физический движок|
| (TypeScript/JS)   |<--->|     (Rust)        |<--->|      (C++)        |
+-------------------+     +-------------------+     +-------------------+
         ^                        ^                         ^
         |                        |                         |
         v                        v                         v
+-------------------+     +-------------------+     +-------------------+
|   Логика игры     |     |   Система ИИ      |     |     Аналитика     |
|    (Python)       |<--->|     (Julia)       |<--->|      (Scala)      |
+-------------------+     +-------------------+     +-------------------+
                                    ^
                                    |
                                    v
                          +-------------------+
                          |    Инструменты    |
                          |  разработки (Go)  |
                          +-------------------+
```

## Методы межъязыкового взаимодействия

Для обеспечения взаимодействия между компонентами, написанными на разных языках программирования, используются следующие подходы:

1. **REST API** - для взаимодействия между клиентом и сервером
2. **WebSocket** - для передачи событий в реальном времени
3. **gRPC** - для высокопроизводительного взаимодействия между серверными компонентами
4. **Shared Memory** - для взаимодействия между физическим движком и сервером
5. **Message Queue (RabbitMQ)** - для асинхронного обмена сообщениями между компонентами
6. **JSON/Protocol Buffers** - для сериализации данных при обмене

## Детали интеграции по компонентам

### 1. Физический движок (C++) и Серверная часть (Rust)

Физический движок предоставляет C API, который используется Rust-сервером через FFI (Foreign Function Interface).

```cpp
// C++ с C API
extern "C" {
    PhysicsWorld* physics_create_world(float gravity_x, float gravity_y);
    void physics_destroy_world(PhysicsWorld* world);
    int physics_add_block(PhysicsWorld* world, float x, float y, float width, float height, float density);
    void physics_update(PhysicsWorld* world, float time_step);
    BlockState* physics_get_blocks_state(PhysicsWorld* world, int* count);
}
```

```rust
// Rust FFI
#[link(name = "physics_engine")]
extern "C" {
    fn physics_create_world(gravity_x: f32, gravity_y: f32) -> *mut PhysicsWorld;
    fn physics_destroy_world(world: *mut PhysicsWorld);
    fn physics_add_block(world: *mut PhysicsWorld, x: f32, y: f32, width: f32, height: f32, density: f32) -> i32;
    fn physics_update(world: *mut PhysicsWorld, time_step: f32);
    fn physics_get_blocks_state(world: *mut PhysicsWorld, count: *mut i32) -> *mut BlockState;
}
```

### 2. Серверная часть (Rust) и Логика игры (Python)

Взаимодействие осуществляется через gRPC, что обеспечивает высокую производительность и типобезопасность.

```proto
// Протокол взаимодействия (Protocol Buffers)
syntax = "proto3";

service GameLogic {
    rpc ProcessMove(MoveRequest) returns (GameStateResponse);
    rpc GenerateNextTetromino(EmptyRequest) returns (TetrominoResponse);
    rpc CheckCollision(CollisionRequest) returns (CollisionResponse);
}

message MoveRequest {
    int32 player_id = 1;
    string move_type = 2;
    int32 tetromino_id = 3;
    float x = 4;
    float y = 5;
    float rotation = 6;
}

message GameStateResponse {
    repeated Block blocks = 1;
    repeated Player players = 2;
    string game_status = 3;
}
```

### 3. Логика игры (Python) и Система ИИ (Julia)

Взаимодействие через REST API с использованием HTTP-запросов и JSON для обмена данными.

```python
# Python (логика игры)
import requests
import json

def get_ai_move(game_state, player_id):
    url = "http://localhost:8001/ai/predict_move"
    payload = {
        "game_state": game_state.to_dict(),
        "player_id": player_id
    }
    response = requests.post(url, json=payload)
    return json.loads(response.text)
```

### 4. Серверная часть (Rust) и Клиентская часть (TypeScript/JS)

Взаимодействие через WebSocket для обновлений в реальном времени и REST API для запросов.

```typescript
// TypeScript (клиент)
class GameClient {
    private socket: WebSocket;
    private apiBaseUrl: string;
    
    constructor(serverUrl: string, apiBaseUrl: string) {
        this.socket = new WebSocket(serverUrl);
        this.apiBaseUrl = apiBaseUrl;
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleServerUpdate(data);
        };
    }
    
    async startGame(gameMode: string): Promise<boolean> {
        const response = await fetch(`${this.apiBaseUrl}/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: gameMode })
        });
        
        return response.ok;
    }
    
    sendMove(moveType: string, x: number, y: number, rotation: number): void {
        this.socket.send(JSON.stringify({
            type: 'move',
            move_type: moveType,
            x: x,
            y: y,
            rotation: rotation
        }));
    }
    
    private handleServerUpdate(data: any): void {
        // Обработка обновлений от сервера
    }
}
```

```rust
// Rust (сервер)
use warp::Filter;
use tokio::sync::mpsc;
use futures::{FutureExt, StreamExt};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct StartGameRequest {
    mode: String,
}

#[derive(Serialize)]
struct GameStateUpdate {
    players: Vec<Player>,
    blocks: Vec<Block>,
    game_status: String,
}

async fn handle_websocket(ws: warp::ws::WebSocket, game_state: Arc<Mutex<GameState>>) {
    // Обработка WebSocket соединения
}

async fn start_game(req: StartGameRequest) -> Result<impl warp::Reply, warp::Rejection> {
    // Обработка запроса на начало игры
}

#[tokio::main]
async fn main() {
    // Настройка маршрутов
    let game_state = Arc::new(Mutex::new(GameState::new()));
    
    let game_state_filter = warp::any().map(move || game_state.clone());
    
    let websocket_route = warp::path("ws")
        .and(warp::ws())
        .and(game_state_filter.clone())
        .map(|ws: warp::ws::Ws, game_state| {
            ws.on_upgrade(move |socket| handle_websocket(socket, game_state))
        });
    
    let start_game_route = warp::path!("game" / "start")
        .and(warp::post())
        .and(warp::body::json())
        .and(game_state_filter.clone())
        .and_then(start_game);
    
    let routes = websocket_route.or(start_game_route);
    
    warp::serve(routes).run(([0, 0, 0, 0], 8000)).await;
}
```

### 5. Система аналитики (Scala) и другие компоненты

Взаимодействие через RabbitMQ для асинхронного сбора данных о событиях игры.

```scala
// Scala (аналитика)
import com.rabbitmq.client._

object AnalyticsConsumer {
  def main(args: Array[String]): Unit = {
    val factory = new ConnectionFactory()
    factory.setHost("localhost")
    val connection = factory.newConnection()
    val channel = connection.createChannel()
    
    channel.queueDeclare("game_events", false, false, false, null)
    
    val consumer = new DefaultConsumer(channel) {
      override def handleDelivery(consumerTag: String, envelope: Envelope, properties: AMQP.BasicProperties, body: Array[Byte]): Unit = {
        val message = new String(body, "UTF-8")
        processGameEvent(message)
      }
    }
    
    channel.basicConsume("game_events", true, consumer)
  }
  
  def processGameEvent(eventJson: String): Unit = {
    // Обработка события игры
  }
}
```

```rust
// Rust (сервер, отправка событий в аналитику)
use lapin::{Connection, ConnectionProperties, Channel, options::*, types::FieldTable};

async fn send_game_event(channel: &Channel, event: &GameEvent) -> Result<(), lapin::Error> {
    let payload = serde_json::to_string(event).unwrap();
    
    channel.basic_publish(
        "",
        "game_events",
        BasicPublishOptions::default(),
        payload.as_bytes(),
        BasicProperties::default(),
    ).await?;
    
    Ok(())
}
```

### 6. Инструменты разработки (Go) и другие компоненты

Инструменты разработки взаимодействуют с другими компонентами через REST API и файловую систему.

```go
// Go (инструменты разработки)
package main

import (
    "encoding/json"
    "io/ioutil"
    "net/http"
    "os"
)

type LevelEditor struct {
    // ...
}

func (le *LevelEditor) SaveLevel(level Level) error {
    data, err := json.MarshalIndent(level, "", "  ")
    if err != nil {
        return err
    }
    
    return ioutil.WriteFile("levels/"+level.Name+".json", data, 0644)
}

func (le *LevelEditor) LoadLevel(name string) (Level, error) {
    data, err := ioutil.ReadFile("levels/" + name + ".json")
    if err != nil {
        return Level{}, err
    }
    
    var level Level
    err = json.Unmarshal(data, &level)
    return level, err
}

func (le *LevelEditor) GetGameState() (GameState, error) {
    resp, err := http.Get("http://localhost:8000/api/game_state")
    if err != nil {
        return GameState{}, err
    }
    defer resp.Body.Close()
    
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        return GameState{}, err
    }
    
    var gameState GameState
    err = json.Unmarshal(body, &gameState)
    return gameState, err
}
```

## Формат обмена данными

Для обеспечения совместимости между различными языками программирования используется единый формат данных на основе JSON:

```json
{
  "game_state": {
    "players": [
      {
        "id": 1,
        "name": "Player 1",
        "tower_blocks": [
          {
            "id": 1,
            "x": 5.0,
            "y": 19.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "color": "#FF0000",
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1,
            "is_static": false
          }
        ],
        "current_tetromino": {
          "type": "I",
          "x": 5.0,
          "y": 0.0,
          "rotation": 0.0
        },
        "next_tetrominos": [
          {
            "type": "J",
            "x": 0.0,
            "y": 0.0,
            "rotation": 0.0
          }
        ],
        "held_tetromino": null,
        "spells": ["REINFORCE", "WIND"],
        "score": 100,
        "health": 3
      }
    ],
    "game_mode": "RACE",
    "current_turn": 1,
    "game_status": "RUNNING",
    "timer": 10.0
  }
}
```

## Схема развертывания

Для упрощения развертывания и обеспечения изоляции компонентов используется Docker и Docker Compose:

```yaml
# docker-compose.yml
version: '3'

services:
  physics_engine:
    build: ./cpp_physics
    ports:
      - "9000:9000"
    volumes:
      - ./shared_memory:/shared_memory
  
  game_server:
    build: ./rust_server
    ports:
      - "8000:8000"
    depends_on:
      - physics_engine
      - game_logic
      - rabbitmq
    environment:
      - PHYSICS_ENGINE_URL=http://physics_engine:9000
      - GAME_LOGIC_URL=http://game_logic:8002
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672
  
  game_logic:
    build: ./python_logic
    ports:
      - "8002:8002"
    depends_on:
      - ai_system
    environment:
      - AI_SYSTEM_URL=http://ai_system:8001
  
  ai_system:
    build: ./julia_ai
    ports:
      - "8001:8001"
  
  analytics_system:
    build: ./scala_analytics
    depends_on:
      - rabbitmq
    environment:
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672
  
  dev_tools:
    build: ./go_tools
    ports:
      - "8003:8003"
    volumes:
      - ./levels:/app/levels
  
  client:
    build: ./typescript_client
    ports:
      - "80:80"
    environment:
      - GAME_SERVER_URL=ws://game_server:8000/ws
      - API_BASE_URL=http://game_server:8000
  
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

## Тестирование интеграции

Для проверки корректности взаимодействия между компонентами используются интеграционные тесты, которые проверяют:

1. Передачу данных между компонентами
2. Корректность сериализации/десериализации
3. Обработку ошибок и граничных случаев
4. Производительность межъязыкового взаимодействия

## Заключение

Данная архитектура обеспечивает сложное взаимодействие между компонентами, написанными на разных языках программирования, сохраняя при этом высокую производительность и масштабируемость системы. Использование различных механизмов межъязыкового взаимодействия позволяет выбрать оптимальный подход для каждой пары компонентов в зависимости от их требований к производительности и типу обмена данными.
