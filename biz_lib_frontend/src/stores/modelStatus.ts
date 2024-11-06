import { defineStore } from 'pinia';
interface ModelDetail {
  name: string,
  type: string,
  id?: number,
  versions: [{
    id?: number,
    version: string,
    base_model: string,
    intro: string,
    sign: string,
    path: string,
    filePath: string,
    public: boolean,
  }]
}
export const modelStore = defineStore('modelStore', {
  state: () => ({
    modelDetail: {
      name: '',
      type: '',
      versions: [{
        version: '',
        base_model: '',
        intro: '',
        sign: '',
        path: '',
        filePath: '',
        public: false,
      }]
    } as ModelDetail,
  }),
  actions: {
    setModelDetail(data: any) {
      this.modelDetail = data;
    },
    clearModelDetail() {
      this.modelDetail = {
        name: '',
        type: '',
        versions: [{
          id: 0,
          version: '',
          base_model: '',
          intro: '',
          sign: '',
          path: '',
          filePath: '',
          public: true,
        }]
      }
    }
  },
});
