import { create } from "zustand"

export const useStore = create(set => ({
    nodes: {},
    results: [],
    logs: {},
    dag: { nodes: [], edges: [] },
    node_progress: {},

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
        })),

    setProgress: (progress) => set(state => ({
        node_progress: {
            ...state.node_progress,
            [progress.node_id]: {
                node_id: progress.node_id ?? "",
                current: progress.current ?? 0,
                total: progress.total ?? 0,
                percent: progress.percent ?? 0,
            }}
        })),
}))