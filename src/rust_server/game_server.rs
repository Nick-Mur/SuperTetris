use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::mpsc;
use tokio::time;
use serde::{Deserialize, Serialize};
use tokio_tungstenite::{accept_async, WebSocketStream};
use futures::{SinkExt, StreamExt};
use tungstenite::protocol::Message;

/**
 * GameServer - Серверная часть для игры Tetris с элементами Tricky Towers
 * Реализовано на Rust с использованием Tokio для асинхронного ввода-вывода
 */

// Типы сообщений между клиентом и сервером
#[derive(Serialize, Deserialize, Debug, Clone)]
enum ClientMessage {
    Join { player_name: String },
    Move { direction: Direction },
    Rotate { direction: RotationDirection },
    Drop,
    UseSpell { spell_type: SpellType, target_player_id: Option<usize> },
    Chat { message: String },
    Disconnect,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
enum ServerMessage {
    GameState { state: GameState },
    PlayerJoined { player_id: usize, player_name: String },
    PlayerLeft { player_id: usize },
    SpellUsed { spell_type: SpellType, caster_id: usize, target_id: Option<usize> },
    ChatMessage { player_id: usize, message: String },
    GameOver { winner_id: Option<usize> },
    Error { message: String },
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum Direction {
    Left,
    Right,
    Down,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum RotationDirection {
    Clockwise,
    CounterClockwise,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum SpellType {
    // Светлая магия
    Reinforce,    // Укрепление блоков
    Stabilize,    // Стабилизация башни
    Enlarge,      // Увеличение блока
    Shrink,       // Уменьшение блока
    Levitate,     // Левитация блока
    
    // Тёмная магия
    Earthquake,   // Землетрясение
    Wind,         // Ветер
    Slippery,     // Скользкие блоки
    Confusion,    // Путаница управления
    Accelerate,   // Ускорение падения
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct GameState {
    players: HashMap<usize, PlayerState>,
    game_mode: GameMode,
    current_turn: usize,
    game_status: GameStatus,
    timer: u32, // Время в секундах
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct PlayerState {
    id: usize,
    name: String,
    tower_blocks: Vec<Block>,
    current_tetromino: Option<Tetromino>,
    next_tetrominos: Vec<Tetromino>,
    held_tetromino: Option<Tetromino>,
    spells: Vec<SpellType>,
    score: u32,
    health: u8, // Для режима выживания
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Block {
    id: usize,
    position: Position,
    size: Size,
    rotation: f32,
    block_type: BlockType,
    properties: BlockProperties,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Tetromino {
    shape: TetrominoShape,
    position: Position,
    rotation: f32,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum TetrominoShape {
    I, J, L, O, S, T, Z,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
struct Position {
    x: f32,
    y: f32,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
struct Size {
    width: f32,
    height: f32,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum BlockType {
    Normal,
    Heavy,
    Light,
    Slippery,
    Sticky,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct BlockProperties {
    is_static: bool,
    density: f32,
    friction: f32,
    restitution: f32,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum GameMode {
    Race,
    Survival,
    Puzzle,
}

#[derive(Serialize, Deserialize, Debug, Clone, Copy)]
enum GameStatus {
    Waiting,
    Running,
    Paused,
    Finished,
}

// Структура для представления клиента
struct Client {
    id: usize,
    name: String,
    sender: mpsc::Sender<ServerMessage>,
}

// Структура для представления сервера
struct GameServer {
    clients: HashMap<usize, Client>,
    game_state: Arc<Mutex<GameState>>,
    next_client_id: usize,
}

impl GameServer {
    fn new() -> Self {
        let game_state = GameState {
            players: HashMap::new(),
            game_mode: GameMode::Race,
            current_turn: 0,
            game_status: GameStatus::Waiting,
            timer: 0,
        };

        GameServer {
            clients: HashMap::new(),
            game_state: Arc::new(Mutex::new(game_state)),
            next_client_id: 1,
        }
    }

    // Добавление нового клиента
    fn add_client(&mut self, name: String, sender: mpsc::Sender<ServerMessage>) -> usize {
        let client_id = self.next_client_id;
        self.next_client_id += 1;

        let client = Client {
            id: client_id,
            name: name.clone(),
            sender,
        };

        self.clients.insert(client_id, client);

        // Добавление игрока в состояние игры
        let mut game_state = self.game_state.lock().unwrap();
        let player_state = PlayerState {
            id: client_id,
            name,
            tower_blocks: Vec::new(),
            current_tetromino: None,
            next_tetrominos: Vec::new(),
            held_tetromino: None,
            spells: Vec::new(),
            score: 0,
            health: 3,
        };

        game_state.players.insert(client_id, player_state);

        // Уведомление всех клиентов о новом игроке
        drop(game_state);
        self.broadcast_player_joined(client_id);

        client_id
    }

    // Удаление клиента
    fn remove_client(&mut self, client_id: usize) {
        self.clients.remove(&client_id);

        // Удаление игрока из состояния игры
        let mut game_state = self.game_state.lock().unwrap();
        game_state.players.remove(&client_id);

        // Уведомление всех клиентов об уходе игрока
        drop(game_state);
        self.broadcast_player_left(client_id);
    }

    // Обработка сообщения от клиента
    fn handle_client_message(&mut self, client_id: usize, message: ClientMessage) {
        match message {
            ClientMessage::Move { direction } => {
                // Обработка движения тетромино
                println!("Player {} moved {:?}", client_id, direction);
                // Здесь будет вызов Python-логики игры
            }
            ClientMessage::Rotate { direction } => {
                // Обработка вращения тетромино
                println!("Player {} rotated {:?}", client_id, direction);
                // Здесь будет вызов Python-логики игры
            }
            ClientMessage::Drop => {
                // Обработка сброса тетромино
                println!("Player {} dropped tetromino", client_id);
                // Здесь будет вызов Python-логики игры
            }
            ClientMessage::UseSpell { spell_type, target_player_id } => {
                // Обработка использования заклинания
                println!("Player {} used spell {:?} on player {:?}", client_id, spell_type, target_player_id);
                // Здесь будет вызов Python-логики игры
                self.broadcast_spell_used(client_id, spell_type, target_player_id);
            }
            ClientMessage::Chat { message } => {
                // Обработка сообщения чата
                println!("Player {} sent message: {}", client_id, message);
                self.broadcast_chat_message(client_id, message);
            }
            ClientMessage::Disconnect => {
                // Обработка отключения клиента
                println!("Player {} disconnected", client_id);
                self.remove_client(client_id);
            }
            _ => {
                println!("Unhandled message from player {}: {:?}", client_id, message);
            }
        }
    }

    // Отправка сообщения конкретному клиенту
    async fn send_message_to_client(&self, client_id: usize, message: ServerMessage) {
        if let Some(client) = self.clients.get(&client_id) {
            if let Err(e) = client.sender.send(message).await {
                println!("Error sending message to client {}: {:?}", client_id, e);
            }
        }
    }

    // Рассылка сообщения всем клиентам
    async fn broadcast_message(&self, message: ServerMessage) {
        for client in self.clients.values() {
            if let Err(e) = client.sender.send(message.clone()).await {
                println!("Error broadcasting message to client {}: {:?}", client.id, e);
            }
        }
    }

    // Рассылка состояния игры всем клиентам
    async fn broadcast_game_state(&self) {
        let game_state = self.game_state.lock().unwrap().clone();
        let message = ServerMessage::GameState { state: game_state };
        self.broadcast_message(message).await;
    }

    // Рассылка уведомления о новом игроке
    fn broadcast_player_joined(&self, player_id: usize) {
        let game_state = self.game_state.lock().unwrap();
        if let Some(player) = game_state.players.get(&player_id) {
            let message = ServerMessage::PlayerJoined {
                player_id,
                player_name: player.name.clone(),
            };
            // Используем блокирующую отправку для простоты примера
            for client in self.clients.values() {
                if let Err(e) = client.sender.blocking_send(message.clone()) {
                    println!("Error broadcasting player joined to client {}: {:?}", client.id, e);
                }
            }
        }
    }

    // Рассылка уведомления об уходе игрока
    fn broadcast_player_left(&self, player_id: usize) {
        let message = ServerMessage::PlayerLeft { player_id };
        // Используем блокирующую отправку для простоты примера
        for client in self.clients.values() {
            if let Err(e) = client.sender.blocking_send(message.clone()) {
                println!("Error broadcasting player left to client {}: {:?}", client.id, e);
            }
        }
    }

    // Рассылка уведомления об использовании заклинания
    fn broadcast_spell_used(&self, caster_id: usize, spell_type: SpellType, target_id: Option<usize>) {
        let message = ServerMessage::SpellUsed {
            spell_type,
            caster_id,
            target_id,
        };
        // Используем блокирующую отправку для простоты примера
        for client in self.clients.values() {
            if let Err(e) = client.sender.blocking_send(message.clone()) {
                println!("Error broadcasting spell used to client {}: {:?}", client.id, e);
            }
        }
    }

    // Рассылка сообщения чата
    fn broadcast_chat_message(&self, player_id: usize, message: String) {
        let server_message = ServerMessage::ChatMessage {
            player_id,
            message,
        };
        // Используем блокирующую отправку для простоты примера
        for client in self.clients.values() {
            if let Err(e) = client.sender.blocking_send(server_message.clone()) {
                println!("Error broadcasting chat message to client {}: {:?}", client.id, e);
            }
        }
    }

    // Запуск игрового цикла
    async fn run_game_loop(&self) {
        let mut interval = time::interval(Duration::from_millis(16)); // ~60 FPS
        
        loop {
            interval.tick().await;
            
            // Обновление состояния игры
            {
                let mut game_state = self.game_state.lock().unwrap();
                if game_state.game_status == GameStatus::Running {
                    // Здесь будет вызов Python-логики игры для обновления состояния
                    game_state.timer += 1;
                }
            }
            
            // Рассылка обновленного состояния игры
            self.broadcast_game_state().await;
        }
    }
}

// Обработка подключения клиента
async fn handle_connection(server: Arc<Mutex<GameServer>>, stream: TcpStream) {
    let addr = stream.peer_addr().unwrap();
    println!("New WebSocket connection: {}", addr);

    let ws_stream = match accept_async(stream).await {
        Ok(ws_stream) => ws_stream,
        Err(e) => {
            println!("Error during WebSocket handshake: {:?}", e);
            return;
        }
    };

    let (mut ws_sender, mut ws_receiver) = ws_stream.split();

    // Канал для отправки сообщений клиенту
    let (sender, mut receiver) = mpsc::channel::<ServerMessage>(100);

    // Получение имени игрока
    let player_name = match ws_receiver.next().await {
        Some(Ok(msg)) => {
            if let Ok(client_msg) = serde_json::from_str::<ClientMessage>(&msg.to_string()) {
                if let ClientMessage::Join { player_name } = client_msg {
                    player_name
                } else {
                    println!("Expected Join message, got: {:?}", client_msg);
                    return;
                }
            } else {
                println!("Failed to parse Join message");
                return;
            }
        }
        _ => {
            println!("Failed to receive Join message");
            return;
        }
    };

    // Добавление клиента в сервер
    let client_id = {
        let mut server = server.lock().unwrap();
        server.add_client(player_name, sender)
    };

    // Задача для отправки сообщений клиенту
    let send_task = tokio::spawn(async move {
        while let Some(message) = receiver.recv().await {
            let json = serde_json::to_string(&message).unwrap();
            if let Err(e) = ws_sender.send(Message::Text(json)).await {
                println!("Error sending message to client {}: {:?}", client_id, e);
                break;
            }
        }
    });

    // Задача для получения сообщений от клиента
    let server_clone = server.clone();
    let receive_task = tokio::spawn(async move {
        while let Some(result) = ws_receiver.next().await {
            match result {
                Ok(msg) => {
                    if msg.is_text() {
                        if let Ok(client_msg) = serde_json::from_str::<ClientMessage>(&msg.to_string()) {
                            let mut server = server_clone.lock().unwrap();
                            server.handle_client_message(client_id, client_msg);
                        }
                    }
                }
                Err(e) => {
                    println!("Error receiving message from client {}: {:?}", client_id, e);
                    break;
                }
            }
        }

        // Клиент отключился
        let mut server = server_clone.lock().unwrap();
        server.remove_client(client_id);
    });

    // Ожидание завершения задач
    tokio::select! {
        _ = send_task => println!("Send task completed for client {}", client_id),
        _ = receive_task => println!("Receive task completed for client {}", client_id),
    }
}

#[tokio::main]
async fn main() {
    let addr = "0.0.0.0:8080";
    let listener = TcpListener::bind(addr).await.expect("Failed to bind");
    println!("Listening on: {}", addr);

    let server = Arc::new(Mutex::new(GameServer::new()));

    // Запуск игрового цикла
    let server_clone = server.clone();
    tokio::spawn(async move {
        let server = server_clone.lock().unwrap();
        server.run_game_loop().await;
    });

    // Обработка подключений
    while let Ok((stream, _)) = listener.accept().await {
        let server_clone = server.clone();
        tokio::spawn(async move {
            handle_connection(server_clone, stream).await;
        });
    }
}
