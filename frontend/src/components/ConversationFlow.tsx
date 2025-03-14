import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '../store/chatStore'
import { useAgentStore } from '../store/agentStore'
import * as d3 from 'd3'

interface FlowLink {
  source: string
  target: string
  value: number
}

interface FlowNode {
  id: string
  name: string
  displayName: string
  emoji: string
}

const ConversationFlow = () => {
  const { messages } = useChatStore()
  const { agents } = useAgentStore()
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })
  
  // 监听窗口大小变化
  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const { width, height } = svgRef.current.getBoundingClientRect()
        setDimensions({ width, height: 300 }) // 固定高度为300px
      }
    }
    
    window.addEventListener('resize', updateDimensions)
    updateDimensions()
    
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])
  
  // 生成对话流数据
  useEffect(() => {
    if (!svgRef.current || messages.length < 2 || dimensions.width === 0) return
    
    // 清除之前的图形
    d3.select(svgRef.current).selectAll('*').remove()
    
    // 准备节点数据
    const nodeMap = new Map<string, FlowNode>()
    
    // 添加所有智能体作为节点
    agents.forEach(agent => {
      nodeMap.set(agent.name, {
        id: agent.name,
        name: agent.name,
        displayName: agent.displayName,
        emoji: agent.emoji
      })
    })
    
    // 添加系统作为节点
    nodeMap.set('System', {
      id: 'System',
      name: 'System',
      displayName: '系统',
      emoji: '🔧'
    })
    
    // 准备链接数据
    const linkMap = new Map<string, FlowLink>()
    
    // 分析消息流向
    for (let i = 1; i < messages.length; i++) {
      const source = messages[i-1].sender
      const target = messages[i].sender
      
      if (source === target) continue // 跳过自己对自己的消息
      
      const linkKey = `${source}-${target}`
      if (linkMap.has(linkKey)) {
        const link = linkMap.get(linkKey)!
        link.value += 1
      } else {
        linkMap.set(linkKey, {
          source,
          target,
          value: 1
        })
      }
    }
    
    const nodes = Array.from(nodeMap.values())
    const links = Array.from(linkMap.values())
    
    // 如果没有链接，不绘制图表
    if (links.length === 0) return
    
    // 设置颜色比例尺
    const colorScale = d3.scaleOrdinal()
      .domain(nodes.map(n => n.id))
      .range(d3.schemeCategory10)
    
    // 创建力导向图
    const simulation = d3.forceSimulation<FlowNode, FlowLink>(nodes)
      .force('link', d3.forceLink<FlowNode, FlowLink>(links)
        .id(d => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
    
    const svg = d3.select(svgRef.current)
    
    // 创建箭头标记
    svg.append('defs').selectAll('marker')
      .data(['end'])
      .enter().append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 30)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999')
    
    // 创建链接
    const link = svg.append('g')
      .selectAll('path')
      .data(links)
      .enter().append('path')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value) * 2)
      .attr('fill', 'none')
      .attr('marker-end', 'url(#arrow)')
    
    // 创建节点组
    const node = svg.append('g')
      .selectAll('.node')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .call(d3.drag<SVGGElement, FlowNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
      )
    
    // 添加节点圆圈
    node.append('circle')
      .attr('r', 25)
      .attr('fill', d => d.id === 'System' ? '#f3f4f6' : colorScale(d.id) as string)
      .attr('stroke', d => d.id === 'System' ? '#9ca3af' : d3.color(colorScale(d.id) as string)?.darker().toString() || '#000')
      .attr('stroke-width', 2)
    
    // 添加节点表情
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '20px')
      .text(d => d.emoji)
    
    // 添加节点标签
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 40)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .text(d => d.displayName)
    
    // 添加链接标签
    svg.append('g')
      .selectAll('text')
      .data(links)
      .enter().append('text')
      .attr('font-size', '10px')
      .attr('text-anchor', 'middle')
      .attr('dy', -5)
      .text(d => d.value > 1 ? d.value.toString() : '')
    
    // 更新模拟
    simulation.on('tick', () => {
      link.attr('d', d => {
        const dx = (d.target as FlowNode).x! - (d.source as FlowNode).x!
        const dy = (d.target as FlowNode).y! - (d.source as FlowNode).y!
        const dr = Math.sqrt(dx * dx + dy * dy) * 2
        return `M${(d.source as FlowNode).x!},${(d.source as FlowNode).y!}A${dr},${dr} 0 0,1 ${(d.target as FlowNode).x!},${(d.target as FlowNode).y!}`
      })
      
      node.attr('transform', d => `translate(${d.x}, ${d.y})`)
      
      svg.selectAll('text:not(.node text)')
        .attr('x', d => {
          const link = d as unknown as FlowLink
          return ((link.source as FlowNode).x! + (link.target as FlowNode).x!) / 2
        })
        .attr('y', d => {
          const link = d as unknown as FlowLink
          return ((link.source as FlowNode).y! + (link.target as FlowNode).y!) / 2
        })
    })
    
    // 拖拽函数
    function dragstarted(event: d3.D3DragEvent<SVGGElement, FlowNode, FlowNode>, d: FlowNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }
    
    function dragged(event: d3.D3DragEvent<SVGGElement, FlowNode, FlowNode>, d: FlowNode) {
      d.fx = event.x
      d.fy = event.y
    }
    
    function dragended(event: d3.D3DragEvent<SVGGElement, FlowNode, FlowNode>, d: FlowNode) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }
    
    // 清理函数
    return () => {
      simulation.stop()
    }
  }, [messages, agents, dimensions])
  
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 h-full">
      <h3 className="text-lg font-medium text-secondary-800 mb-4">对话流向图</h3>
      {messages.length < 2 ? (
        <div className="flex items-center justify-center h-64 text-secondary-500">
          需要至少两条消息才能生成对话流向图
        </div>
      ) : (
        <svg ref={svgRef} width="100%" height="300" />
      )}
    </div>
  )
}

export default ConversationFlow 