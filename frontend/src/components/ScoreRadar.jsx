import {
  Radar, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts"

export default function ScoreRadar({ scores }) {

  const data = Object.entries(scores).map(([k, v]) => ({
    name: k,
    value: v
  }))


  return (
    <ResponsiveContainer width="100%" height={160}>
      <RadarChart cx="50%" cy="50%" outerRadius="60%" data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="name" />
        <PolarRadiusAxis
          domain={[0, 1]}
          angle={30}
          tickCount={5}
        />
        <Radar
          name="评分"
          dataKey="value"
          stroke="#8884d8"
          fill="#8884d8"
          fillOpacity={0.6}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}