export interface Model {
  id: string
  name: string
  type: string
  versions?: ModelVersion[]
  user_id: string
  user_name: string
  counter?:any
}

export interface ModelVersion {
  available: boolean
  version: string
  base_model: string 
  bizy_model_id: number
  sign:string
  path:string
  counter:any
  intro:string
  created_at: string
  file_name: string
  file_size:number
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
