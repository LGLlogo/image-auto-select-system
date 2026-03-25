import { Handle, Position } from 'reactflow';
import { Progress } from 'antd';
export default function DagNode({ data }) {
    // 多色渐变配置
    // 根据进度值动态设置颜色
    const getProgressColor = (percentValue) => {
        if (percentValue < 30) {
            return '#f30d0dbf'; // 红色
        } else if (percentValue < 70) {
            return '#faad14'; // 黄色
        } else {
            return '#32e10a'; // 绿色
        }
    };
    return (
        <div style={{
            padding: 10,
            border: '1px solid #ccc',
            borderRadius: 6,
            background: data?.status === "done" ? "#ace58f" :
                data?.status === "running" ? "#69aeef" :
                    data?.status === "fail" ? "#ff4d4f" :
                        "#ccc",
            minWidth: 160
        }}>
            {/* 左进右出（横向 DAG） */}
            <Handle type="target" position={Position.Left} />
            <Handle type="source" position={Position.Right} />

            <div style={{ fontWeight: 'bold' }}>
                {data.label}
            </div>

            {/* 状态 */}
            <div style={{ fontSize: 12 }}>
                状态: {data.status}
            </div>

            {/* 进度条 */}
            <Progress percent={data.progress} strokeColor={getProgressColor(data.progress)} status="active" />

            {/* <div style={{
                marginTop: 6,
                height: 6,
                background: '#fcf5f5',
                borderRadius: 3,
                overflow: 'hidden'
            }}>
                <div style={{
                    width: `${data.progress || 0}%`,
                    height: '100%',
                    background: getProgressColor(data.progress)
                }} />
            </div> */}
        </div>
    );
}