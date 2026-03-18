import { useState } from "react"
import DagViewer from "./components/DagViewer"
import ResultTable from "./components/ResultTable"
import LogPanel from "./components/LogPanel"
import { runPipeline } from "./api"
import useWS from "./useWS"

export default function App() {
  useWS()
  const [dir, setDir] = useState("")
  const start = () => {
    runPipeline(dir)
  }

  return (

    <div style={{ padding: 20 }}>

      <h2>AI 自动选片系统</h2>

      <input
        value={dir}
        onChange={e => setDir(e.target.value)}
        placeholder="输入图片文件夹路径"
      />

      <button onClick={start}>开始运行</button>

      <h3>DAG监控</h3>

      <DagViewer />

      {/* <h3>选片结果</h3> */}


      <LogPanel />
      <ResultTable />

    </div>
  )
}