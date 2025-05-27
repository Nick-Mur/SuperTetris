import '@testing-library/jest-dom';
import '@testing-library/jest-dom/extend-expect';

// Мок для WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  onclose: (() => void) | null = null;
  readyState: number = WebSocket.CONNECTING;

  constructor(url: string) {
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      this.onopen?.();
    }, 0);
  }

  send(data: string) {
    // Мок для отправки данных
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    this.onclose?.();
  }
}

// Мок для requestAnimationFrame
const mockRAF = (callback: FrameRequestCallback) => {
  return setTimeout(callback, 0);
};

const mockCAF = (id: number) => {
  clearTimeout(id);
};

// Глобальные моки
global.WebSocket = MockWebSocket as any;
global.requestAnimationFrame = mockRAF;
global.cancelAnimationFrame = mockCAF;

// Мок для ResizeObserver
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = MockResizeObserver as any; 