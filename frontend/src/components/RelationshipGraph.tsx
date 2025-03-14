import { useRef, useEffect, useState } from 'react'
import * as d3 from 'd3'
import { useAgentStore } from '../store/agentStore'
import { useChatStore } from '../store/chatStore'

interface Node extends d3.SimulationNodeDatum {
  id: string
  name: string
  displayName: string
  emoji: string
  messageCount: number
  group?: number
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: string | Node
  target: string | Node
  relationship: string
  value: number
}

const RelationshipGraph = () => {
  const svgRef = useRef<SVGSVGElement>(null)
  const { agents } = useAgentStore()
  const { messages } = useChatStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [minInteractions, setMinInteractions] = useState(0)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [zoomLevel, setZoomLevel] = useState(1)
  
  useEffect(() => {
    if (!svgRef.current) return
    
    // 清除之前的图形
    d3.select(svgRef.current).selectAll("*").remove()
    
    // 计算消息统计
    const messageCounts: Record<string, number> = {}
    const interactionCounts: Record<string, Record<string, number>> = {}
    
    agents.forEach(agent => {
      messageCounts[agent.name] = 0
      interactionCounts[agent.name] = {}
      
      agents.forEach(otherAgent => {
        if (agent.name !== otherAgent.name) {
          interactionCounts[agent.name][otherAgent.name] = 0
        }
      })
    })
    
    // 统计消息数量
    messages.forEach(message => {
      if (messageCounts[message.sender] !== undefined) {
        messageCounts[message.sender]++
      }
    })
    
    // 统计交互次数
    let lastSender = ''
    messages.forEach(message => {
      if (lastSender && lastSender !== message.sender) {
        if (interactionCounts[lastSender] && interactionCounts[lastSender][message.sender] !== undefined) {
          interactionCounts[lastSender][message.sender]++
        }
      }
      lastSender = message.sender
    })
    
    // 创建节点数据
    const nodes: Node[] = agents.map((agent, index) => ({
      id: agent.name,
      name: agent.name,
      displayName: agent.displayName,
      emoji: agent.emoji,
      messageCount: messageCounts[agent.name] || 0,
      group: index % 5 // 将智能体分为5个组，用于颜色区分
    }))
    
    // 创建连接数据
    const links: Link[] = []
    
    agents.forEach(agent => {
      agents.forEach(otherAgent => {
        if (agent.name !== otherAgent.name) {
          const interactionCount = interactionCounts[agent.name][otherAgent.name]
          
          // 只添加有交互的连接，或者有关系定义的连接
          if (interactionCount > minInteractions || (agent.relationships && agent.relationships[otherAgent.displayName])) {
            links.push({
              source: agent.name,
              target: otherAgent.name,
              relationship: agent.relationships?.[otherAgent.displayName] || '交互',
              value: Math.max(1, interactionCount) // 确保至少有1的值，以便显示
            })
          }
        }
      })
    })
    
    // 过滤节点和连接
    let filteredNodes = nodes
    let filteredLinks = links
    
    // 搜索过滤
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      filteredNodes = nodes.filter(node => 
        node.name.toLowerCase().includes(searchLower) || 
        node.displayName.toLowerCase().includes(searchLower)
      )
      
      const nodeIds = new Set(filteredNodes.map(n => n.id))
      filteredLinks = links.filter(link => 
        nodeIds.has(typeof link.source === 'string' ? link.source : link.source.id) && 
        nodeIds.has(typeof link.target === 'string' ? link.target : link.target.id)
      )
    }
    
    // 选中智能体过滤
    if (selectedAgent) {
      const connectedNodeIds = new Set<string>()
      connectedNodeIds.add(selectedAgent)
      
      links.forEach(link => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id
        const targetId = typeof link.target === 'string' ? link.target : link.target.id
        
        if (sourceId === selectedAgent) {
          connectedNodeIds.add(targetId)
        } else if (targetId === selectedAgent) {
          connectedNodeIds.add(sourceId)
        }
      })
      
      filteredNodes = nodes.filter(node => connectedNodeIds.has(node.id))
      filteredLinks = links.filter(link => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id
        const targetId = typeof link.target === 'string' ? link.target : link.target.id
        return connectedNodeIds.has(sourceId) && connectedNodeIds.has(targetId)
      })
    }
    
    // 获取SVG尺寸
    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight
    
    // 创建缩放行为
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform)
        setZoomLevel(event.transform.k)
      })
    
    svg.call(zoom)
    
    // 创建容器
    const container = svg.append('g')
    
    // 创建力导向模拟
    const simulation = d3.forceSimulation<Node, Link>(filteredNodes)
      .force('link', d3.forceLink<Node, Link>(filteredLinks).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => Math.sqrt(d.messageCount || 1) * 5 + 20))
    
    // 颜色比例尺
    const color = d3.scaleOrdinal(d3.schemeCategory10)
    
    // 创建连接
    const link = container.append('g')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(filteredLinks)
      .join('line')
      .attr('stroke-width', d => Math.sqrt(d.value) + 1)
      .attr('stroke', '#999')
      
    // 创建节点
    const node = container.append('g')
      .selectAll('.node')
      .data(filteredNodes)
      .join('g')
      .attr('class', 'node')
      .call(d3.drag<SVGGElement, Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('click', (event, d) => {
        setSelectedAgent(selectedAgent === d.id ? null : d.id)
      })
    
    // 添加圆形背景
    node.append('circle')
      .attr('r', d => Math.sqrt(d.messageCount || 1) * 5 + 15)
      .attr('fill', d => color(d.group?.toString() || '0'))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .attr('opacity', 0.8)
    
    // 添加表情符号
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '16px')
      .attr('class', 'node-text')
      .text(d => d.emoji)
    
    // 添加名称标签
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('dy', d => Math.sqrt(d.messageCount || 1) * 5 + 25)
      .attr('font-size', '12px')
      .attr('fill', '#333')
      .attr('class', 'node-text')
      .text(d => d.displayName)
    
    // 添加消息数量标签
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('dy', d => Math.sqrt(d.messageCount || 1) * 5 + 40)
      .attr('font-size', '10px')
      .attr('fill', '#666')
      .attr('class', 'node-text')
      .text(d => `消息: ${d.messageCount}`)
    
    // 添加连接标签
    container.append('g')
      .selectAll('text')
      .data(filteredLinks)
      .join('text')
      .attr('class', 'link-text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '10px')
      .attr('fill', '#666')
      .attr('stroke', 'white')
      .attr('stroke-width', '2px')
      .attr('paint-order', 'stroke')
      .attr('opacity', 0.9)
      .text(d => d.relationship)
      .each(function(d) {
        const sourceX = typeof d.source === 'string' ? 0 : d.source.x || 0
        const sourceY = typeof d.source === 'string' ? 0 : d.source.y || 0
        const targetX = typeof d.target === 'string' ? 0 : d.target.x || 0
        const targetY = typeof d.target === 'string' ? 0 : d.target.y || 0
        
        const x = (sourceX + targetX) / 2
        const y = (sourceY + targetY) / 2
        
        d3.select(this).attr('transform', `translate(${x}, ${y})`)
      })
    
    // 更新模拟
    simulation.on('tick', () => {
      link
        .attr('x1', d => typeof d.source === 'string' ? 0 : d.source.x || 0)
        .attr('y1', d => typeof d.source === 'string' ? 0 : d.source.y || 0)
        .attr('x2', d => typeof d.target === 'string' ? 0 : d.target.x || 0)
        .attr('y2', d => typeof d.target === 'string' ? 0 : d.target.y || 0)
      
      node.attr('transform', d => `translate(${d.x || 0}, ${d.y || 0})`)
      
      // 更新连接标签位置
      container.selectAll('.link-text')
        .each(function(d: any) {
          if (!d) return
          
          const sourceX = typeof d.source === 'string' ? 0 : d.source.x || 0
          const sourceY = typeof d.source === 'string' ? 0 : d.source.y || 0
          const targetX = typeof d.target === 'string' ? 0 : d.target.x || 0
          const targetY = typeof d.target === 'string' ? 0 : d.target.y || 0
          
          const x = (sourceX + targetX) / 2
          const y = (sourceY + targetY) / 2
          
          d3.select(this).attr('transform', `translate(${x}, ${y})`)
        })
    })
    
    // 拖拽函数
    function dragstarted(event: d3.D3DragEvent<SVGGElement, Node, Node>, d: Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }
    
    function dragged(event: d3.D3DragEvent<SVGGElement, Node, Node>, d: Node) {
      d.fx = event.x
      d.fy = event.y
    }
    
    function dragended(event: d3.D3DragEvent<SVGGElement, Node, Node>, d: Node) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }
    
    // 初始缩放以适应屏幕
    const initialScale = Math.min(width, height) / Math.max(width, height) * 0.9
    svg.call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(initialScale).translate(-width / 2, -height / 2))
    
    return () => {
      simulation.stop()
    }
  }, [agents, messages, searchTerm, minInteractions, selectedAgent])
  
  const handleZoomIn = () => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    const zoom = d3.zoom<SVGSVGElement, unknown>()
    svg.transition().call(zoom.scaleBy, 1.2)
  }
  
  const handleZoomOut = () => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    const zoom = d3.zoom<SVGSVGElement, unknown>()
    svg.transition().call(zoom.scaleBy, 0.8)
  }
  
  const handleReset = () => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    const zoom = d3.zoom<SVGSVGElement, unknown>()
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight
    const initialScale = Math.min(width, height) / Math.max(width, height) * 0.9
    svg.transition().call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(initialScale).translate(-width / 2, -height / 2))
  }
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-wrap gap-2 mb-4">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索智能体..."
            className="input w-full"
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-sm text-secondary-600">最小交互次数:</span>
          <input
            type="range"
            min="0"
            max="10"
            value={minInteractions}
            onChange={(e) => setMinInteractions(parseInt(e.target.value))}
            className="w-24"
          />
          <span className="text-sm text-secondary-600">{minInteractions}</span>
        </div>
        
        <div className="flex items-center space-x-1">
          <button 
            onClick={handleZoomOut}
            className="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
            title="缩小"
          >
            -
          </button>
          <span className="text-sm text-secondary-600">{Math.round(zoomLevel * 100)}%</span>
          <button 
            onClick={handleZoomIn}
            className="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
            title="放大"
          >
            +
          </button>
          <button 
            onClick={handleReset}
            className="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200 ml-1"
            title="重置视图"
          >
            重置
          </button>
        </div>
      </div>
      
      <div className="relative flex-1 border border-gray-200 rounded-lg overflow-hidden">
        <svg ref={svgRef} width="100%" height="100%" className="bg-gray-50"></svg>
        
        <div className="absolute bottom-2 left-2 bg-white bg-opacity-80 p-2 rounded-md text-xs">
          <p>提示:</p>
          <ul className="list-disc list-inside">
            <li>点击智能体可以筛选相关连接</li>
            <li>拖动智能体可以调整位置</li>
            <li>滚轮可以缩放视图</li>
            <li>节点大小表示消息数量</li>
            <li>连线粗细表示交互频率</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default RelationshipGraph 