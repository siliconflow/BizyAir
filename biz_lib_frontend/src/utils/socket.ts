export class WebSocketClient {
  private url: string;
  private protocols: string | string[];
  private reconnectDelay: number;
  private maxReconnectDelay: number;
  private keepAliveInterval: number;
  private ws: WebSocket | null;
  private keepAliveTimer: NodeJS.Timeout | null;
  private reconnectTimer: NodeJS.Timeout | null;

  constructor(url: string, protocols: string | string[]) {
    this.url = url;
    this.protocols = protocols;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
    this.keepAliveInterval = 10000;
    this.ws = null;
    this.keepAliveTimer = null;
    this.reconnectTimer = null;

    this.connect();
  }

  connect() {
    this.ws = new WebSocket(this.url, this.protocols);
    this.ws.onopen = () => {
      this.onOpen();
    };

    this.ws.onmessage = (message: MessageEvent) => {
      if (message.data !== 'pong') {
        this.onMessage(message);
      }
    };

    this.ws.onerror = (error: Event) => {
      this.onError(error);
    };

    this.ws.onclose = () => {
      console.warn('The WebSocket connection has been closed and is ready to be reconnected');
      this.onClose();
      this.scheduleReconnect();
    };
  }

  startKeepAlive() {
    if (this.keepAliveTimer) return;

    this.keepAliveTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send('ping');
      }
    }, this.keepAliveInterval);
  }

  stopKeepAlive() {
    if (this.keepAliveTimer) {
      clearInterval(this.keepAliveTimer);
      this.keepAliveTimer = null;
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setTimeout(() => {
      console.log(`Attempt to reconnect...`);
      this.connect();
      this.reconnectTimer = null;

      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }, this.reconnectDelay);
  }

  onOpen() {
    this.reconnectDelay = 2000;
    this.startKeepAlive();
  }

  onMessage(message: MessageEvent) {
    const data = JSON.parse(message.data);
    if (data === 'pong') {
      // Do nothing
    } else {
      console.log('message:', data);
    }
  }

  onError(error: Event) {
    console.error('WebSocket Error: ', error);
  }

  onClose() {
    this.stopKeepAlive();
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
    this.stopKeepAlive();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}
