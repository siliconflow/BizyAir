export interface Model {
  name: string
  version: string
  baseModel: string
  status: string
  isPublic?: boolean
  isCheckpoint?: boolean
  versions?: ModelVersion[]
}

export interface ModelVersion {
  version: string
  baseModel: string 
  status: string
}

export interface FilterState {
  mode: 'my' | 'my_fork' | 'publicity'
  keyword: string
  modelTypes: string[]
  baseModels: string[]
  sort: 'recently' | 'most-forked' | 'most-used'
}