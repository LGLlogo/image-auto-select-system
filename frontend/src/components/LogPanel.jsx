import { useStore } from "../store"
import { Table } from "antd"

export default function LogPanel(){

 const logs = useStore(s=>s.logs)

    const sorted = [...logs].sort((a, b) => new Date(b.time) - new Date(a.time))

    const columns = [
        { title: "Time", dataIndex: "time" },
        { title: "Msg", dataIndex: "msg" },
    ]

    return <Table columns={columns} dataSource={sorted} />

}