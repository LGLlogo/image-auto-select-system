import { create } from "zustand"

export const useStore = create(set => ({
    nodes: {},
    results: [],
    logs: [],
    dag: { nodes: [], edges: [] },

    setState: (data) => set({
        nodes: data.nodes,
        results: data.results,
        logs: data.logs,
        dag: data.dag
    })
}))