import { BarChart, Bar, XAxis, YAxis } from "recharts"

export default function WeightChart({ weights }) {

  const data = Object.entries(weights).map(([k, v]) => ({
    name: k,
    value: v
  }))

  return (
    <BarChart width={300} height={200} data={data}>
      <XAxis dataKey="name" />
      <YAxis />
      <Bar dataKey="value" />
    </BarChart>
  )
}