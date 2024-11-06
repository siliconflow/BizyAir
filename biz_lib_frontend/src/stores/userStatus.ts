import { defineStore } from 'pinia';
import { getUserInfo } from '@/api/user'
import { WebSocketClient } from '@/utils/socket.ts'

export const useStatusStore = defineStore('userStatus', {
  state: () => ({
    isLogin: false,
    socketMessage: {},
  }),
  actions: {
    loginRefresh() {
      getUserInfo().then((info: { data: any; }) => {
        sessionStorage.setItem('userInfo', JSON.stringify(info.data))
        this.isLogin = true
      }).catch(() => {
        this.isLogin = false
      })
    },
    sendSocket() {
      const wsClient = new WebSocketClient(`ws://${location.host}/bizyair/ws?clientId=${sessionStorage.getItem('clientId')}`, []);
      wsClient.onMessage = message => {
          // notifySubscribers('socketMessage', message);
          console.log('socketMessage', message)
          const res = JSON.parse(message.data);
          this.socketMessage = res;
          if (res && res.type === 'errors') {
              // toast.error(res.data.message)
              console.error(res.data.message)
          }
      }
    }
  },
});
