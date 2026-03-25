import { Table, Image } from "antd"
import { useStore } from "../store"
import { getImgPreview,getThumbPreview } from "../api"

export default function ResultTable() {

    const results = useStore(s => s.results)

    const sorted = [...results].sort((a, b) => b.total_score - a.total_score)

    const formatScore = (v, n = 2) =>
        v == null ? "-" : v.toFixed(n)

    const columns = [
        { title: "File", dataIndex: "file" },
        {
            title: "Img",
            dataIndex: "img",
            render: (v, row, idx) => {
                return (
                        <Image
                            key={idx}
                            width={200}
                            src={getThumbPreview(`${formatScore(row.total_score, 3)}_${row.file}`)}
                            loading="lazy"
                            preview={{
                                src: getImgPreview(`${formatScore(row.total_score, 3)}_${row.file}`),
                                visible: false,
                                mask: '点击查看大图',
                                onOpenChange: (visible) => console.log(visible),
                            }}
                        />
                )
            }

        },
        { title: "Final", dataIndex: "total_score", render: (v) => formatScore(v, 3) },
        { title: "Quality", dataIndex: "quality_score", render: (v) => formatScore(v, 3) },
        { title: "Commercial", dataIndex: "commercial_value", render: (v) => formatScore(v, 3) },
        { title: "Technical", dataIndex: "technical_quality", render: (v) => formatScore(v, 3) },
        { title: "Composition", dataIndex: "composition_quality", render: (v) => formatScore(v, 3) },
        { title: "Post", dataIndex: "post_processing", render: (v) => formatScore(v, 3) },
        { title: "Content", dataIndex: "content_uniqueness", render: (v) => formatScore(v, 3) },
        { title: "Negative", dataIndex: "negative_quality", render: (v) => formatScore(v, 3) },
    ]

    return <Image.PreviewGroup>
        <Table columns={columns} dataSource={sorted} />
    </Image.PreviewGroup>
}