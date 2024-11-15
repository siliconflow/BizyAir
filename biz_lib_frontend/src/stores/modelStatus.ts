import { Model, ModelVersion as ModelVersionType } from '@/types/model';
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
  file_name?: string;
}

interface ModelDetail {
  name: string;
  nameError?: boolean;
  type: string;
  typeError?: boolean;
  id?: number;
  versions: ModelVersion[];
}
type ShowVersionId = number | undefined;
export const modelStore = defineStore('modelStore', {
  state: () => ({
    modelDetail: {
      name: '',
      type: '',
      versions: []
    } as ModelDetail,
    showDialog: false,
    reloadModelSelectList:false, // reload model select list
    closeModelSelectDialog:false, // close model select dialog
    closeModelDetailDialog:false, // close model detail dialog
    showVersionId: 0 as ShowVersionId,
    mode: 'my' as 'my' | 'my_fork' | 'publicity',
    applyObject:{version: {} as ModelVersionType, model: {} as Model},
    reload: 0
  }),
  actions: {
    setModelDetail(data: any) {
      this.modelDetail = data;
      if (this.modelDetail.id) {
        this.modelDetail.versions.forEach((item: ModelVersion) => {
          item.filePath = item.file_name as string;
        })
      }
    },
    clearModelDetail() {
      this.modelDetail = {
        name: '',
        type: '',
        versions: []
      }
    },
    setDialogStatus(status: boolean, versionId?: number) {
      this.showDialog = status;
      this.showVersionId = versionId;
    },
    uploadModelDone() {
      this.reload += 1;
    },
    closeAndReload() {
      this.closeModelDetailDialog=true;
      this.reloadModelSelectList =true;
    },
    setApplyObject(version: ModelVersionType, model: Model) {
      this.closeModelSelectDialog=true;
      this.closeModelDetailDialog=true;
      this.applyObject = {version, model};
    }
  },
});
