import axios from "axios"

export const API="http://localhost:8000"

export const runPipeline=(dir)=>{
 return axios.post(`${API}/run`,{image_dir:dir})
}

export const getState=()=>{
 return axios.get(`${API}/dag_state`)
}