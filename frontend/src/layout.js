import dagre from "dagre"

export function layout(nodes, edges) {
  const nodeWidth = 150
  const nodeHeight = 50
  
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ 
    rankdir: "LR",
  //  // 添加其他图属性
    nodesep: 50,
    edgesep: 30,
    ranksep: 100
  })
  nodes.forEach(n => {
    if (!n.id) return
    g.setNode(n.id, { width: nodeWidth, height: nodeHeight })
  })
  edges.forEach(e => {
    if (!e.source || !e.target) return
    if (!g.hasNode(e.source) || !g.hasNode(e.target)) {
      console.warn("Invalid edge:", e)
      return
    }
    g.setEdge(e.source, e.target)
  })
  // console.log(g)
  dagre.layout(g)

  return nodes.map(n => {
    const pos = g.node(n.id)
    if (!pos) {
      return {
        ...n,
        position: { x: 0, y: 0 }
      }
    }
    // console.log(`${n.id}-${pos.x}-${pos.y}`)
    return {
      ...n,
      position: { 
        x: pos.x - nodeWidth / 2, 
        y: pos.y - nodeHeight / 2 
      }
    }
  })
}