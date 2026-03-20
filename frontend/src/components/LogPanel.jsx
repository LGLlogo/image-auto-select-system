import { useStore } from "../store"
import { Table } from "antd"

export default function LogPanel() {

    const logs = useStore(s => s.logs)
    const keys = Object.keys(logs)
    // console.log(logs, keys)
    
    const logsTable = []
    for (const k of keys) {
        logsTable.push(...logs[k])
    }
    // console.log(logsTable)
    
    const sorted = [...logsTable].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

    const columns = [
        { title: "time", dataIndex: "timestamp", onCell: (v) => new Date(v) },
        { title: "task_id", dataIndex: "task_id" },
        { title: "node", dataIndex: "node" },
        { title: "message", dataIndex: "message" },
    ]

    return <Table columns={columns} dataSource={sorted} />

}