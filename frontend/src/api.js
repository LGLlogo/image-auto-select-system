import axios from "axios"

export const API = "http://localhost:8000"

export const runPipeline=(dir)=>{
 return axios.post(`${API}/run`,{image_dir:dir})
}

export const getThumbPreview = (name) => {
    return `${API}/thumb?file_name=${name}`
}

export const getImgPreview = (name) => {
    return `${API}/image?file_name=${name}`
}