import { useEffect } from "react"
import { useStore } from "./store"

export default function useWS() {

    const setState = useStore(s => s.setState)

    useEffect(() => {

        const ws = new WebSocket("ws://localhost:8000/ws")

        ws.onmessage = (e) => {
            setState(JSON.parse(e.data))
        }

        return () => ws.close()

    }, [])
}