
import { useStore } from "../store"
import { Progress } from 'antd';

export default function NodePanel({ selectedNode }) {
    const nodes = useStore(s => s.nodes)
    const progress = useStore(s => s.node_progress)
    if (!selectedNode) return <div>暂无数据</div>
    // console.log(node)
    const target_node = nodes[selectedNode.id]
    const node_progress = progress[selectedNode.id]
    // console.log(node_process)

    // 计算保留两位小数的进度值
    const getRoundedPercent = (value) => {
        return Math.round(value * 100) / 100;
    };

    return (
        <div>

            <h3>节点信息</h3>

            <p>状态: {target_node?.status}</p>
            <p>当前进度: {getRoundedPercent(node_progress?.percent)}%</p>
            <Progress percent={getRoundedPercent(node_progress?.percent)} status="active" type="circle" />

            <p>图片数: {target_node?.image_count}</p>

            <pre style={{ maxHeight: 300, overflow: "auto" }}>
                {JSON.stringify(target_node?.scores, null, 2)}
            </pre>

        </div>
    )
}