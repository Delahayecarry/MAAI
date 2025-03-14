import { useEffect, useRef } from 'react'
import { useChatStore } from '../store/chatStore'
import { useAgentStore } from '../store/agentStore'
import * as d3 from 'd3'

const MessageTimeline = () => {
  const { messages } = useChatStore()
  const { agents } = useAgentStore()
  const svgRef = useRef<SVGSVGElement>(null)
  
  useEffect(() => {
    if (!svgRef.current || messages.length < 2) return
    
    // 清除之前的图形
    d3.select(svgRef.current).selectAll('*').remove()
    
    // 设置尺寸和边距
    const margin = { top: 20, right: 30, bottom: 30, left: 40 }
    const width = svgRef.current.clientWidth - margin.left - margin.right
    const height = 200 - margin.top - margin.bottom
    
    // 创建SVG
    const svg = d3.select(svgRef.current)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)
    
    // 准备数据
    const timeData = messages.map(msg => {
      const agent = agents.find(a => a.name === msg.sender) || { name: msg.sender, displayName: msg.sender === 'System' ? '系统' : msg.sender, emoji: '🤖' }
      return {
        timestamp: new Date(msg.timestamp),
        sender: msg.sender,
        senderDisplayName: agent.displayName,
        emoji: agent.emoji
      }
    })
    
    // 设置颜色比例尺
    const colorScale = d3.scaleOrdinal()
      .domain([...new Set(timeData.map(d => d.sender))])
      .range(d3.schemeCategory10)
    
    // 设置X轴比例尺（时间）
    const timeExtent = d3.extent(timeData, d => d.timestamp) as [Date, Date]
    const xScale = d3.scaleTime()
      .domain(timeExtent)
      .range([0, width])
    
    // 添加X轴
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(5).tickFormat(d => {
        const date = d as Date
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      }))
    
    // 添加Y轴标签（仅用于说明）
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '10px')
      .text('消息发送时间')
    
    // 添加时间线
    svg.append('line')
      .attr('x1', 0)
      .attr('y1', height / 2)
      .attr('x2', width)
      .attr('y2', height / 2)
      .attr('stroke', '#e5e7eb')
      .attr('stroke-width', 2)
    
    // 添加消息点
    const circles = svg.selectAll('.message-point')
      .data(timeData)
      .enter()
      .append('g')
      .attr('class', 'message-point')
      .attr('transform', d => `translate(${xScale(d.timestamp)},${height / 2})`)
    
    // 添加消息点的圆圈
    circles.append('circle')
      .attr('r', 8)
      .attr('fill', d => d.sender === 'System' ? '#6b7280' : colorScale(d.sender) as string)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
    
    // 添加消息点的表情
    circles.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '10px')
      .text(d => d.emoji)
    
    // 添加消息点的提示信息
    circles.append('title')
      .text(d => `${d.senderDisplayName} - ${d.timestamp.toLocaleTimeString()}`)
    
    // 添加连接线
    svg.selectAll('.message-line')
      .data(timeData.slice(1))
      .enter()
      .append('line')
      .attr('class', 'message-line')
      .attr('x1', (d, i) => xScale(timeData[i].timestamp))
      .attr('y1', height / 2)
      .attr('x2', d => xScale(d.timestamp))
      .attr('y2', height / 2)
      .attr('stroke', '#d1d5db')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '3,3')
    
    // 添加时间间隔标记
    for (let i = 1; i < timeData.length; i++) {
      const prev = timeData[i-1].timestamp
      const curr = timeData[i].timestamp
      const diffMs = curr.getTime() - prev.getTime()
      const diffSec = diffMs / 1000
      
      // 只显示超过2秒的间隔
      if (diffSec > 2) {
        svg.append('text')
          .attr('x', (xScale(prev) + xScale(curr)) / 2)
          .attr('y', height / 2 - 15)
          .attr('text-anchor', 'middle')
          .attr('font-size', '9px')
          .attr('fill', '#6b7280')
          .text(`${diffSec.toFixed(1)}秒`)
      }
    }
    
    // 添加标题
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 0 - margin.top / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .text('消息时间线')
  }, [messages, agents])
  
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-lg font-medium text-secondary-800 mb-4">消息时间线</h3>
      {messages.length < 2 ? (
        <div className="flex items-center justify-center h-40 text-secondary-500">
          需要至少两条消息才能生成时间线
        </div>
      ) : (
        <svg ref={svgRef} width="100%" height="200" />
      )}
    </div>
  )
}

export default MessageTimeline 