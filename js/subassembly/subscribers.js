const subscribers = new Map();

// 订阅消息
export function subscribe(key, callback) {
  if (!subscribers.has(key)) {
    subscribers.set(key, []);
  }
  subscribers.get(key).push(callback);
}

// 取消订阅消息
export function unsubscribe(key, callback) {
  if (subscribers.has(key)) {
    const index = subscribers.get(key).indexOf(callback);
    if (index > -1) {
      subscribers.get(key).splice(index, 1);
    }
  }
}

// 通知订阅者
export function notifySubscribers(key, data) {
  if (subscribers.has(key)) {
    subscribers.get(key).forEach(callback => callback(data));
  }
}
