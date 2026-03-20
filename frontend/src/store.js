import { create } from "zustand"

export const useStore = create(set => ({
    nodes: {},
    results: [],
    logs: {},
    dag: { nodes: [], edges: [] },

    setState: (data) => set({
        nodes: data.nodes ?? {},
        results: data.results ?? [],
        dag: data.dag ?? { nodes: [], edges: [] }
    }),

    addLog: (log) =>
        set(state => ({
            logs: {
                ...state.logs,
                [log.task_id]: [
                    ...(state.logs[log.task_id] || []),
                    log
                ]
            }
        }))
}))