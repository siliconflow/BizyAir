import { defineStore } from 'pinia';
interface ModelDetail {
  name: string,
  type: string,
  id?: number,
  versions: []
}
export const modelStore = defineStore('modelStore', {
  state: () => ({
    modelDetail: {
      name: '',
      type: ''
    } as ModelDetail,
  }),
  actions: {
    setModelDetail(data: any) {
      this.modelDetail = data;
    },
    clearModelDetail() {
      this.modelDetail = {
        name: '',
        type: ''
      }
    }
  },
});
