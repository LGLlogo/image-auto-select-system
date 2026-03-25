import { useEffect } from "react"
import { useStore } from "./store"

export default function useWS(taskId) {
    console.log(taskId)
    const setState = useStore(s => s.setState)
    const addLog = useStore(s => s.addLog)
    const setProgress = useStore(s => s.setProgress)

    useEffect(() => {
        if (taskId) {
            const ws = new WebSocket(`ws://localhost:8000/ws/${taskId}`)
            ws.onmessage = (e) => {
                const state = JSON.parse(e.data)
                if (state.type === "log") {
                    addLog(state)
                }
                else if (state.type === "process") {
                    setProgress(state)
                }
                else {
                    setState(state)
                }
                // console.log(state.results)
            }
            // return () => ws.close()
        }

    }, [setState, addLog, taskId])
}