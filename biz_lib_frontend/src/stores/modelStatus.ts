import { defineStore } from 'pinia';
interface ModelVersion {
  id?: number;
  version: string;
  base_model: string;
  intro: string;
  sign: string;
  path: string;
  filePath: string;
  public: boolean;
}

interface ModelDetail {
  name: string;
  type: string;
  id?: number;
  versions: ModelVersion[];
}
export const modelStore = defineStore('modelStore', {
  state: () => ({
    modelDetail: {
      name: '',
      type: '',
      versions: []
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
        versions: []
      }
    }
  },
});
