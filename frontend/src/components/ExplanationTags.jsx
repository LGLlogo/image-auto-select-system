import { Tag } from "antd"

export default function ExplanationTags({ explanation }) {
  return (
    <>
      {explanation.map((e, i) => (
        <Tag key={i} color="blue">{e}</Tag>
      ))}
    </>
  )
}