import { Table, Image, Popover, Button, Tag } from "antd"
import { useStore } from "../store"
import { getImgPreview, getThumbPreview } from "../api"
import ExplanationTags from "./ExplanationTags"
import ScoreRadar from './ScoreRadar';
import WeightChart from './WeightChart';

export default function ResultTable() {

    const results = useStore(s => s.results)

    const sorted = [...results].sort((a, b) => b.total_score - a.total_score)

    const formatScore = (v, n = 2) => {
        let score = v== null ? "-" : v.toFixed(n)
        let color = 'black'; // 默认颜色

        if (score >= 0.6) {
            color = 'green';
            // 也可以返回一个 Tag 组件，视觉效果更好
            return <Tag color={color}>{score}</Tag>;
        } else if (score >= 0.4) {
            color = 'orange';
            return <Tag color={color}>{score}</Tag>;
        } else {
            color = 'red';
            return <Tag color={color}>{score}</Tag>;
        }
    }

    const columns = [
        {
            title: "Name",
            dataIndex: "name",
            render: (v, row, idx) => {
                return (
                    <Popover
                        placement="right"
                        bodyStyle={{ padding: '20px', width: 432 }}
                        content={
                            <div>
                                <Image
                                    key={idx}
                                    width={200}
                                    src={getThumbPreview(`${formatScore(row.total_score, 3)}_${row.name}`)}
                                    loading="lazy"
                                    preview={{
                                        src: getImgPreview(`${formatScore(row.total_score, 3)}_${row.name}`),
                                        visible: false,
                                        mask: '点击查看大图',
                                        onOpenChange: (open) => console.log(open),
                                    }}
                                />
                                <ScoreRadar scores={row.sub_scores} />
                                <WeightChart weights={row.weights} />
                                <ExplanationTags explanation={row.explanation} />
                            </div>
                        }
                        title={`${v} Details`}
                        trigger="click"
                    >
                        <div>
                            <Button>{v}</Button>
                        </div>
                    </Popover>
                )
            }
        },
        // {
        //     title: "Img",
        //     dataIndex: "img",
        //     render: (v, row, idx) => {
        //         return (
        //                 <Image
        //                     key={idx}
        //                     width={200}
        //                     src={getThumbPreview(`${formatScore(row.total_score, 3)}_${row.file}`)}
        //                     loading="lazy"
        //                     preview={{
        //                         src: getImgPreview(`${formatScore(row.total_score, 3)}_${row.file}`),
        //                         visible: false,
        //                         mask: '点击查看大图',
        //                         onOpenChange: (visible) => console.log(visible),
        //                     }}
        //                 />
        //         )
        //     }

        // },
        { title: "Final", dataIndex: "total_score", render: (v) => formatScore(v, 3) },
        { title: "Quality", dataIndex: "quality_score", render: (v, row) => formatScore(row.sub_scores["quality_score"], 3) },
        { title: "Aesthetic", dataIndex: "aesthetic_score", render: (v, row) => formatScore(row.sub_scores["aesthetic_score"], 3) },
        { title: "Commercial", dataIndex: "commercial_value", render: (v, row) => formatScore(row.sub_scores["commercial_value"], 3) },
        { title: "Technical", dataIndex: "technical_quality", render: (v, row) => formatScore(row.sub_scores["technical_quality"], 3) },
        { title: "Composition", dataIndex: "composition_quality", render: (v, row) => formatScore(row.sub_scores["composition_quality"], 3) },
        { title: "Post", dataIndex: "post_processing", render: (v, row) => formatScore(row.sub_scores["post_processing"], 3) },
        { title: "Content", dataIndex: "content_uniqueness", render: (v, row) => formatScore(row.sub_scores["content_uniqueness"], 3) },
        { title: "Negative", dataIndex: "negative_quality", render: (v, row) => formatScore(row.sub_scores["negative_quality"], 3) },
    ]

    return <Image.PreviewGroup>
        <Table columns={columns} dataSource={sorted} />
    </Image.PreviewGroup>
}