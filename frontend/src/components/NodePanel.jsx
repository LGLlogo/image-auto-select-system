import React from "react";
import { Drawer, Tag } from "antd";
import { useStore } from "../store";
import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer
} from "recharts";

export default function NodePanel({ selectedNode }) {
    const nodes = useStore((s) => s.nodes);

    const node = selectedNode ? nodes[selectedNode.id] : null;
    // console.log(selectedNode, node)
    if (!node) return null;

    const scores = node.scores || {};
    const images = Object.keys(scores)
    console.log(scores[images[0]])
    

    const radarData = [
        { name: "商业", value: scores[images[0]].commercial_value || 0 },
        { name: "美学", value: scores[images[0]].aesthetic_score || 0 },
        { name: "技术", value: scores[images[0]].technical_quality || 0 },
        { name: "后期", value: scores[images[0]].post_processing || 0 },
        { name: "构图", value: scores[images[0]].composition_quality || 0 },
        { name: "可用性", value: scores[images[0]].content_uniqueness || 0 },
    ];

    const tags = scores.tags || [];

    return (
        <div>

            {/* 基本信息 */}
            <div style={{ marginBottom: 16 }}>
                <p>状态: {node.status}</p>
                <p>图片数: {node.image_count}</p>
            </div>

            {/* 雷达图 */}
            <div style={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="name" />
                        <PolarRadiusAxis domain={[0, 10]} />
                        <Radar dataKey="value" />
                    </RadarChart>
                </ResponsiveContainer>
            </div>

            {/* 标签 */}
            <div style={{ marginTop: 20 }}>
                <h3>内容标签</h3>
                {tags.map((t, i) => (
                    <Tag key={i}>{t}</Tag>
                ))}
            </div>

            {/* 图片预览 */}
            <div style={{ marginTop: 20 }}>
                <h3>图片预览</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                    {(images || []).slice(0, 4).map((img, i) => (
                        <img
                            key={i}
                            src={img}
                            alt="preview"
                            style={{ width: "100%", borderRadius: 6 }}
                        />
                    ))}
                </div>
            </div>

            {/* 原始分数 */}
            <div style={{ marginTop: 20 }}>
                <h3>原始数据</h3>
                <pre style={{ maxHeight: 200, overflow: "auto" }}>
                    {JSON.stringify(scores, null, 2)}
                </pre>
            </div>
        </div>
    );
}
