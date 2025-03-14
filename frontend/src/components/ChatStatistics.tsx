import { useEffect, useState } from 'react'
import { useChatStore } from '../store/chatStore'
import { useAgentStore } from '../store/agentStore'
import { motion } from 'framer-motion'
import * as d3 from 'd3'

interface AgentStats {
  name: string
  displayName: string
  messageCount: number
  color: string
  emoji: string
}

const ChatStatistics = () => {
  const { messages, isSimulationRunning } = useChatStore()
  const { agents } = useAgentStore()
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [elapsedTime, setElapsedTime] = useState<number>(0)
  const [agentStats, setAgentStats] = useState<AgentStats[]>([])
  
  // 设置颜色比例尺
  const colorScale = d3.scaleOrdinal()
    .domain(agents.map(a => a.name))
    .range(d3.schemeCategory10)
  
  // 当模拟开始时记录开始时间
  useEffect(() => {
    if (isSimulationRunning && !startTime) {
      setStartTime(new Date())
    } else if (!isSimulationRunning) {
      setStartTime(null)
      setElapsedTime(0)
    }
  }, [isSimulationRunning, startTime])
  
  // 计算经过的时间
  useEffect(() => {
    let timer: number
    
    if (isSimulationRunning && startTime) {
      timer = window.setInterval(() => {
        const now = new Date()
        const elapsed = Math.floor((now.getTime() - startTime.getTime()) / 1000)
        setElapsedTime(elapsed)
      }, 1000)
    }
    
    return () => {
      if (timer) clearInterval(timer)
    }
  }, [isSimulationRunning, startTime])
  
  // 计算每个智能体的消息数量
  useEffect(() => {
    const stats: Record<string, number> = {}
    
    // 初始化所有智能体的消息计数为0
    agents.forEach(agent => {
      stats[agent.name] = 0
    })
    
    // 统计系统消息
    stats['System'] = 0
    
    // 计算每个智能体的消息数量
    messages.forEach(message => {
      if (stats[message.sender] !== undefined) {
        stats[message.sender]++
      }
    })
    
    // 转换为数组并排序
    const statsArray: AgentStats[] = Object.entries(stats).map(([name, count]) => {
      const agent = agents.find(a => a.name === name)
      return {
        name,
        displayName: agent?.displayName || (name === 'System' ? '系统' : name),
        messageCount: count,
        color: name === 'System' ? '#6b7280' : colorScale(name) as string,
        emoji: agent?.emoji || (name === 'System' ? '🔧' : '🤖')
      }
    }).sort((a, b) => b.messageCount - a.messageCount)
    
    setAgentStats(statsArray)
  }, [messages, agents, colorScale])
  
  // 格式化时间
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }
  
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 h-full">
      <h3 className="text-lg font-medium text-secondary-800 mb-4">对话统计</h3>
      
      <div className="space-y-6">
        {/* 基本统计信息 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-primary-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-primary-600">{messages.length}</div>
            <div className="text-sm text-secondary-600">总消息数</div>
          </div>
          
          <div className="bg-primary-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-primary-600">
              {isSimulationRunning ? formatTime(elapsedTime) : '00:00'}
            </div>
            <div className="text-sm text-secondary-600">对话时长</div>
          </div>
        </div>
        
        {/* 智能体消息统计 */}
        <div>
          <h4 className="text-sm font-medium text-secondary-700 mb-2">智能体发言统计</h4>
          <div className="space-y-2">
            {agentStats.map(stat => (
              <motion.div 
                key={stat.name}
                initial={{ width: 0 }}
                animate={{ width: `${stat.messageCount ? (stat.messageCount / Math.max(...agentStats.map(s => s.messageCount))) * 100 : 0}%` }}
                transition={{ duration: 0.5 }}
                className="flex items-center"
              >
                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center mr-2">
                  <span className="text-xl">{stat.emoji}</span>
                </div>
                <div className="flex-grow">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-secondary-700">{stat.displayName}</span>
                    <span className="text-sm text-secondary-500">{stat.messageCount}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="h-2.5 rounded-full" 
                      style={{ 
                        width: `${stat.messageCount ? (stat.messageCount / Math.max(...agentStats.map(s => s.messageCount))) * 100 : 0}%`,
                        backgroundColor: stat.color
                      }}
                    ></div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
        
        {/* 对话状态 */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${isSimulationRunning ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-secondary-700">
              {isSimulationRunning ? '对话进行中' : '对话未开始或已结束'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatStatistics 