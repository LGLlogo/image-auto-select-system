import { useEffect } from "react"
import { useStore } from "./store"

export default function useWS(taskId) {
    console.log(taskId)
    const setState = useStore(s => s.setState)

    useEffect(() => {
        if (taskId) {
            const ws = new WebSocket(`ws://localhost:8000/ws/${taskId}`)
            ws.onmessage = (e) => {
                const state = JSON.parse(e.data)
                // console.log(state.results)
                setState(state)
            }
            // return () => ws.close()
        }

    }, [setState, taskId])
}