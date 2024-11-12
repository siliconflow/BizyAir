import { defineStore } from 'pinia';
interface ModelVersion {
  id?: number;
  version: string;
  versionError?: boolean;
  base_model: string;
  baseModelError?: boolean;
  intro: string;
  sign: string;
  path: string;
  filePath: string;
  filePathError?: boolean;
  public: boolean;
  progress?: number;
  file_upload_id?: string;
}

interface ModelDetail {
  name: string;
  nameError?: boolean;
  type: string;
  typeError?: boolean;
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
