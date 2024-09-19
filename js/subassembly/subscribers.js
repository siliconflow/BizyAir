const subscribers = new Map();

export function subscribe(key, callback) {
  if (!subscribers.has(key)) {
    subscribers.set(key, []);
  }
  subscribers.get(key).push(callback);
}

export function unsubscribe(key, callback) {
  if (subscribers.has(key)) {
    const index = subscribers.get(key).indexOf(callback);
    if (index > -1) {
      subscribers.get(key).splice(index, 1);
    }
  }
}

export function notifySubscribers(key, data) {
  if (subscribers.has(key)) {
    subscribers.get(key).forEach(callback => callback(data));
  }
}
