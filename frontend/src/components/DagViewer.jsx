import { useState } from "react"
import { ReactFlow, ReactFlowProvider } from "reactflow"
import "reactflow/dist/style.css"
import { useStore } from "../store"
import { layout } from "../layout"
import NodePanel from "./NodePanel"
import DagNode from './DagNode';
import { Drawer } from "antd"

export default function DagViewer() {
    const [selectedNode, setSelectedNode] = useState(null)
    const [open, setOpen] = useState(false)
    const progress = useStore(s => s.node_progress)

     // 计算保留两位小数的进度值
    const getRoundedPercent = (value) => {
        return Math.round(value * 100) / 100;
    };

    // 👇 点击节点
    const handleNodeClick = (event, node) => {
        setSelectedNode(node)
        setOpen(true)
    }
    const nodeTypes = {
        dagNode: DagNode,
    };

    const { dag, nodes } = useStore()

    const rfNodes = layout(
        dag.nodes.map(n => ({
            id: n.id,
            type: 'dagNode', // 指定类型
            data: {
                label: n.label,
                status: nodes[n.id]?.status,
                progress: getRoundedPercent(progress[n.id]?.percent)
            },
            // sourcePosition: 'right', //  从右边出
            // targetPosition: 'left',  //  从左边进
            // style: {
            //     background:
            // nodes[n.id]?.status === "done" ? "#16a34a" :
            //     nodes[n.id]?.status === "running" ? "#2563eb" :
            //         nodes[n.id]?.status === "fail" ? "#f2460d" :
            //             "#6b7280",
            //     color: "#fff",
            //     borderRadius: 30,
            //     padding: 16
            // }
        })),
        dag.edges
    )


    const rfEdges = dag.edges.map(e => ({
        id: `${e.source}-${e.target}`,
        source: e.source,
        target: e.target,
        animated: true, // 数据流动效果
        // type: 'smoothstep',
    }))

    return (
        <div style={{ height: 400, border: "1px solid red" }}>
            <ReactFlowProvider>
                <ReactFlow key={nodes.length} nodes={rfNodes} edges={rfEdges}
                    nodeTypes={nodeTypes}
                    onNodeClick={handleNodeClick}
                />
            </ReactFlowProvider>
            {/* 右边 Panel */}
            <Drawer
                title={selectedNode?.data?.label || "节点详情"}
                placement="right"
                open={open}
                onClose={() => { setOpen(false) }}
                size={500}>
                <NodePanel selectedNode={selectedNode} />
            </Drawer>


        </div>
    )
}