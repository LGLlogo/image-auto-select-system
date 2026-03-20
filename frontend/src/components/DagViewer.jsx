import { useState } from "react"
import { ReactFlow, ReactFlowProvider } from "reactflow"
import "reactflow/dist/style.css"
import { useStore } from "../store"
import { layout } from "../layout"
import NodePanel from "./NodePanel"
import { Drawer } from "antd"

export default function DagViewer() {
    const [selectedNode, setSelectedNode] = useState(null)
    const [open, setOpen] = useState(false)
    
    // 👇 点击节点
    const handleNodeClick = (event, node) => {
    setSelectedNode(node)
    setOpen(true)
    }


    const { dag, nodes } = useStore()

    const rfNodes = layout(
        dag.nodes.map(n => ({
            id: n.id,
            data: { label: n.label },
            style: {
                background:
                    nodes[n.id]?.status === "done" ? "#16a34a" :
                        nodes[n.id]?.status === "running" ? "#2563eb" :
                        nodes[n.id]?.status === "fail" ? "#f2460d": 
                            "#6b7280",
                color: "#fff",
                borderRadius: 30,
                padding: 16
            }
        })),
        dag.edges
    )
    

    const rfEdges = dag.edges.map(e => ({
        id: `${e.source}-${e.target}`,
        source: e.source,
        target: e.target
    }))

    return (
        <div style={{ height: 400, border: "1px solid red" }}>
                <ReactFlowProvider>
                    <ReactFlow key={nodes.length} nodes={rfNodes} edges={rfEdges}
                        onNodeClick={handleNodeClick}
                    />
                </ReactFlowProvider>
            {/* 右边 Panel */}
                <Drawer
                    title={selectedNode?.data?.label || "节点详情"}
                    placement="right"
                    open={open} 
                    onClose={() => {setOpen(false)}}
                    size={500}>
                    <NodePanel selectedNode={selectedNode}  />
                </Drawer>


        </div>
    )
}