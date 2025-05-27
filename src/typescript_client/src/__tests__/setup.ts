import '@testing-library/jest-dom';
import { setupMocks, clearMocks } from './mocks';

beforeAll(() => {
  setupMocks();
});

beforeEach(() => {
  clearMocks();
});

afterAll(() => {
  jest.restoreAllMocks();
});

// Mock ResizeObserver
class MockResizeObserver {
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
}

Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: MockResizeObserver,
});

// Mock requestAnimationFrame
Object.defineProperty(window, 'requestAnimationFrame', {
  writable: true,
  value: (callback: FrameRequestCallback) => {
    callback(0);
    return 0;
  },
});

Object.defineProperty(window, 'cancelAnimationFrame', {
  writable: true,
  value: jest.fn(),
});

// Mock WebSocket
class MockWebSocket {
  send = jest.fn();
  close = jest.fn();
  addEventListener = jest.fn();
  removeEventListener = jest.fn();
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
}

Object.defineProperty(window, 'WebSocket', {
  writable: true,
  value: MockWebSocket,
});

// Mock fetch
Object.defineProperty(window, 'fetch', {
  writable: true,
  value: jest.fn(),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn()
} as unknown as Storage;

Object.defineProperty(window, 'localStorage', {
  writable: true,
  value: localStorageMock,
});

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn()
} as unknown as Storage;

Object.defineProperty(window, 'sessionStorage', {
  writable: true,
  value: sessionStorageMock,
});

// Mock Audio
class MockAudio {
  play = jest.fn();
  pause = jest.fn();
  load = jest.fn();
}

Object.defineProperty(window, 'Audio', {
  writable: true,
  value: MockAudio,
});

// Mock Image
class MockImage {
  src = '';
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
}

Object.defineProperty(window, 'Image', {
  writable: true,
  value: MockImage,
});

// Mock Canvas
class MockCanvas {
  getContext = jest.fn((contextId: '2d' | 'bitmaprenderer' | 'webgl' | 'webgl2', options?: any) => {
    if (contextId === '2d') {
      return {
        fillRect: jest.fn(),
        clearRect: jest.fn(),
        getImageData: jest.fn(),
        putImageData: jest.fn(),
        createImageData: jest.fn(),
        setTransform: jest.fn(),
        drawImage: jest.fn(),
        save: jest.fn(),
        fillText: jest.fn(),
        restore: jest.fn(),
        beginPath: jest.fn(),
        moveTo: jest.fn(),
        lineTo: jest.fn(),
        closePath: jest.fn(),
        stroke: jest.fn(),
        translate: jest.fn(),
        scale: jest.fn(),
        rotate: jest.fn(),
        arc: jest.fn(),
        fill: jest.fn(),
        measureText: jest.fn(() => ({
          width: 0
        })),
        transform: jest.fn(),
        rect: jest.fn(),
        clip: jest.fn(),
        canvas: document.createElement('canvas'),
        getContextAttributes: jest.fn(),
        globalAlpha: 1,
        globalCompositeOperation: 'source-over',
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'low',
        shadowBlur: 0,
        shadowColor: 'black',
        shadowOffsetX: 0,
        shadowOffsetY: 0,
        lineCap: 'butt',
        lineDashOffset: 0,
        lineJoin: 'miter',
        lineWidth: 1,
        miterLimit: 10,
        textAlign: 'start',
        textBaseline: 'alphabetic',
        direction: 'inherit',
        font: '10px sans-serif',
        filter: 'none'
      } as unknown as CanvasRenderingContext2D;
    } else if (contextId === 'bitmaprenderer') {
      return {
        transferFromImageBitmap: jest.fn()
      } as unknown as ImageBitmapRenderingContext;
    }
    return null;
  }) as unknown as typeof HTMLCanvasElement.prototype.getContext;
}

Object.defineProperty(window.HTMLCanvasElement.prototype, 'getContext', {
  writable: true,
  value: MockCanvas.prototype.getContext,
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
  }))
}); 