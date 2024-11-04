export interface Model {
  id: string
  name: string
  type: string
  versions?: ModelVersion[]
}

export interface ModelVersion {
  available: boolean
  version: string
  base_model: string 
  bizy_model_id: number
  counter:any
  created_at: string
  file_name: string
  id:number
  public:boolean
  updated_at:string
}


export interface ModelListPathParams {
  current: number
  page_size: number
  mode: string
  total:number
 
}

export interface FilterState {
  keyword: string
  model_types: string[]
  base_models: string[]
  sort:'Recently' | 'Most Forked' | 'Most Used'
}

export interface CommonModelType {
  label: string
  value: string
}
