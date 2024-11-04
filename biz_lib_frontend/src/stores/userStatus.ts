import { defineStore } from 'pinia';
import { getUserInfo } from '@/api/user'

export const useStatusStore = defineStore('userStatus', {
  state: () => ({
    isLogin: false,
  }),
  actions: {
    loginRefresh() {
      getUserInfo().then((info: { data: any; }) => {
        sessionStorage.setItem('userInfo', JSON.stringify(info.data))
        this.isLogin = true
      }).catch(() => {
        this.isLogin = false
      })
    }
  },
});
