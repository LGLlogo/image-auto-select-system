import { Table } from "antd"
import { useStore } from "../store"

export default function ResultTable() {

    const results = useStore(s => s.results)

    const sorted = [...results].sort((a, b) => b.total_score - a.total_score)

    const formatScore = (v, n = 2) =>
    v == null ? "-" : v.toFixed(n)

    const columns = [
        { title: "File", dataIndex: "file" },
        { title: "Final", dataIndex: "total_score", render: (v) => formatScore(v, 3) },
        { title: "Quality", dataIndex: "quality_score", render: (v) => formatScore(v, 3) },
        { title: "Commercial", dataIndex: "commercial_value", render: (v) => formatScore(v, 3) },
        { title: "Technical", dataIndex: "technical_quality", render: (v) => formatScore(v, 3) },
        { title: "Composition", dataIndex: "composition_quality", render: (v) => formatScore(v, 3) },
        { title: "Post", dataIndex: "post_processing", render: (v) => formatScore(v, 3) },
        { title: "Content", dataIndex: "content_uniqueness", render: (v) => formatScore(v, 3) },
        { title: "Negative", dataIndex: "negative_quality", render: (v) => formatScore(v, 3) },
    ]

    return <Table columns={columns} dataSource={sorted} />
}