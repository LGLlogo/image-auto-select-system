
import { useStore } from "../store"

export default function NodePanel({ selectedNode }) {
    const nodes = useStore(s => s.nodes)
    if (!selectedNode) return <div>暂无数据</div>
    // console.log(node)
    const target_node = nodes[selectedNode.id]

    return (
        <div>

            <h3>节点信息</h3>

            <p>状态: {target_node?.status}</p>
            <p>图片数: {target_node?.image_count}</p>

            <pre style={{ maxHeight: 300, overflow: "auto" }}>
                {JSON.stringify(target_node?.scores, null, 2)}
            </pre>

        </div>
    )
}