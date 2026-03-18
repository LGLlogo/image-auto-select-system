import { Table } from "antd"
import { useStore } from "../store"

export default function ResultTable() {

    const results = useStore(s => s.results)

    const sorted = [...results].sort((a, b) => b.total_score - a.total_score)

    const columns = [
        { title: "File", dataIndex: "file" },
        { title: "Final", dataIndex: "total_score" },
        { title: "Quality", dataIndex: "quality_score" },
        { title: "Commercial", dataIndex: "commercial_value" },
        { title: "Technical", dataIndex: "technical_quality" },
        { title: "Composition", dataIndex: "composition_quality" },
        { title: "Post", dataIndex: "post_processing" },
        { title: "Content", dataIndex: "content_uniqueness" },
        { title: "Negative", dataIndex: "negative_quality" },
    ]

    return <Table columns={columns} dataSource={sorted} />
}