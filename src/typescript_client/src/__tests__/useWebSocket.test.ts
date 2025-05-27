import { renderHook, act } from '@testing-library/react-hooks';
import { useWebSocket } from '../hooks/useWebSocket';

// Определяем интерфейс для мокированного экземпляра WebSocket
interface MockWebSocketInstance {
  url: string | URL;
  readyState: number; // Оставим как number, попробуем решить через приведение типа
  send: jest.Mock;
  close: jest.Mock;
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  addEventListener: jest.Mock;
  removeEventListener: jest.Mock;
}

describe('useWebSocket Hook', () => {
  const mockUrl = 'ws://localhost:8080';
  const mockOnGameStateUpdate = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Мокаем глобальный WebSocket, чтобы контролировать его в тестах
    // Приводим тип к Jest mock для лучшей типизации
    global.WebSocket = jest.fn().mockImplementation((url) => {
      const instance: Partial<WebSocket> = { // Используем Partial для гибкости
        url,
        readyState: WebSocket.CONNECTING,
        send: jest.fn(),
        close: jest.fn(),
        onopen: null,
        onmessage: null,
        onerror: null,
        onclose: null,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
      };

      // Делаем readyState доступным для записи в моке
      Object.defineProperty(instance, 'readyState', {
        writable: true,
        value: WebSocket.CONNECTING,
      });

      return instance as WebSocket; // Приводим возвращаемый тип к WebSocket
    }) as unknown as jest.MockedClass<typeof WebSocket>; // Приводим тип мока конструктора

    // Мокаем события WebSocket, чтобы их можно было имитировать
    // @ts-ignore: window is a global
    window.dispatchEvent = jest.fn((event) => {
      // Обращаемся к мокированному экземпляру через mock.instances[0]
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (!mockWs) return;

      // Явные проверки на существование обработчиков событий
      if (event.type === 'message') {
        // @ts-ignore: event has data
        if (typeof event.data === 'string' && mockWs.onmessage) {
          // @ts-ignore: onmessage expects MessageEvent
          mockWs.onmessage(event);
        }
      } else if (event.type === 'error') {
        if (mockWs.onerror) {
          // @ts-ignore: onerror expects Event
          mockWs.onerror(event);
        }
      } else if (event.type === 'close') {
        if (mockWs.onclose) {
          // @ts-ignore: onclose expects CloseEvent
          mockWs.onclose(event);
        }
      }
    });
  });

  it('connects to WebSocket and handles messages', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onGameStateUpdate: mockOnGameStateUpdate,
        onError: mockOnError,
        onClose: mockOnClose,
      })
    );

    // Ожидаем, что WebSocket был создан автоматически
    expect(global.WebSocket).toHaveBeenCalledWith(mockUrl);

    // Simulate WebSocket open event
    act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onopen) {
        mockWs.onopen(new Event('open'));
      }
    });

    // Simulate WebSocket message
    const mockMessage = { type: 'gameStateUpdate', data: { score: 100 } }; // Используем правильный тип
    act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onmessage) {
        const messageEvent = new MessageEvent('message', {
          data: JSON.stringify(mockMessage),
        });
        mockWs.onmessage(messageEvent);
      }
    });

    expect(mockOnGameStateUpdate).toHaveBeenCalledWith(mockMessage.data);
  });

  it('handles WebSocket errors', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onGameStateUpdate: mockOnGameStateUpdate,
        onError: mockOnError,
        onClose: mockOnClose,
      })
    );

     // Ожидаем, что WebSocket был создан автоматически
     expect(global.WebSocket).toHaveBeenCalledWith(mockUrl);

    // Simulate WebSocket error
    act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onerror) {
        const errorEvent = new Event('error');
        mockWs.onerror(errorEvent);
      }
    });

    expect(mockOnError).toHaveBeenCalled();
  });

  it('handles WebSocket close', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onGameStateUpdate: mockOnGameStateUpdate,
        onError: mockOnError,
        onClose: mockOnClose,
      })
    );

    // Ожидаем, что WebSocket был создан автоматически
    expect(global.WebSocket).toHaveBeenCalledWith(mockUrl);

    // Simulate WebSocket close
    act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onclose) {
        const closeEvent = new CloseEvent('close');
        mockWs.onclose(closeEvent);
      }
    });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('sends messages through WebSocket', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onGameStateUpdate: mockOnGameStateUpdate,
        onError: mockOnError,
        onClose: mockOnClose,
      })
    );

    // Simulate WebSocket open to allow sending messages
     act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onopen) {
        mockWs.onopen(new Event('open'));
        // Устанавливаем readyState в OPEN после открытия
        // @ts-ignore: Allow assigning to read-only property in mock
        mockWs.readyState = WebSocket.OPEN;
      }
    });

    const mockMessage = { type: 'move', direction: 'left' };
    act(() => {
      result.current.sendMessage(mockMessage);
    });

    // Verify that the message was sent
    expect((global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0].send).toHaveBeenCalledWith(
      JSON.stringify(mockMessage)
    );
  });

  it('cleans up WebSocket connection on unmount', () => {
    const { unmount } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onGameStateUpdate: mockOnGameStateUpdate,
        onError: mockOnError,
        onClose: mockOnClose,
      })
    );

     // Simulate WebSocket open to allow closing
     act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onopen) {
        mockWs.onopen(new Event('open'));
        // Устанавливаем readyState в OPEN после открытия
        // @ts-ignore: Allow assigning to read-only property in mock
        mockWs.readyState = WebSocket.OPEN;
      }
    });

    unmount();

    expect((global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0].close).toHaveBeenCalled();
  });

  it('reconnects when connection is lost', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onGameStateUpdate: mockOnGameStateUpdate,
        onError: mockOnError,
        onClose: mockOnClose,
      })
    );

    // Ожидаем первое соединение
    expect(global.WebSocket).toHaveBeenCalledTimes(1);

    // Simulate connection loss
    act(() => {
      const mockWs = (global.WebSocket as jest.MockedClass<typeof WebSocket>).mock.instances[0];
      if (mockWs && mockWs.onclose) {
        const closeEvent = new CloseEvent('close');
        mockWs.onclose(closeEvent);
      }
    });

    // Verify that a reconnection attempt was made
    expect(global.WebSocket).toHaveBeenCalledTimes(2);
  });
});