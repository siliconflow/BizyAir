export class WebSocketClient {
  constructor(url, protocols) {
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

    this.ws.onmessage = (message) => {
      if (message.data !== 'pong') {
        this.onMessage(message);
      };
    };


    this.ws.onerror = (error) => {
      this.onError(error);
    };


    this.ws.onclose = () => {
      console.warn('WebSocket 连接已关闭，准备重连');
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
      console.log(`尝试重新连接...`);
      this.connect();
      this.reconnectTimer = null;

      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }, this.reconnectDelay);
  }

  onOpen() {

    this.reconnectDelay = 2000;
    this.startKeepAlive();
  }

  onMessage(message) {

    const data = JSON.parse(message.data);
    if (data === 'pong') {
    } else {
      console.log('message:', data);
    }
  }

  onError(error) {

    console.error('WebSocket 错误: ', error);
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
