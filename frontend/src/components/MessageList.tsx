import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '../store/chatStore'
import MessageItem from './MessageItem'
import { format, isToday, isYesterday, isSameDay } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { motion, AnimatePresence } from 'framer-motion'

// 消息分组接口
interface MessageGroup {
  date: Date
  messages: {
    id: string
    sender: string
    senderDisplayName: string
    content: string
    timestamp: string
    isTyping?: boolean
    isQueued?: boolean
  }[]
}

const MessageList = () => {
  const { messages } = useChatStore()
  const [messageGroups, setMessageGroups] = useState<MessageGroup[]>([])
  const [autoScroll, setAutoScroll] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const lastScrollHeightRef = useRef<number>(0)
  const lastMessagesLengthRef = useRef<number>(0)
  
  // 当组件挂载时记录日志
  useEffect(() => {
    console.log('MessageList组件已挂载')
    return () => {
      console.log('MessageList组件已卸载')
    }
  }, [])
  
  // 将消息按日期分组
  useEffect(() => {
    if (messages.length === 0) {
      setMessageGroups([])
      return
    }
    
    const groups: MessageGroup[] = []
    let currentGroup: MessageGroup | null = null
    
    messages.forEach(message => {
      const messageDate = new Date(message.timestamp)
      
      // 如果是第一条消息或者日期与上一组不同，创建新组
      if (!currentGroup || !isSameDay(messageDate, currentGroup.date)) {
        if (currentGroup) {
          groups.push(currentGroup)
        }
        currentGroup = {
          date: messageDate,
          messages: []
        }
      }
      
      // 将消息添加到当前组
      if (currentGroup) {
        currentGroup.messages.push(message)
      }
    })
    
    // 添加最后一组
    if (currentGroup) {
      groups.push(currentGroup)
    }
    
    setMessageGroups(groups)
    
    // 记录消息数量变化
    lastMessagesLengthRef.current = messages.length
  }, [messages])
  
  // 自动滚动到底部
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      // 记录滚动前的高度
      if (containerRef.current) {
        lastScrollHeightRef.current = containerRef.current.scrollHeight
      }
      
      // 滚动到底部
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messageGroups, autoScroll])
  
  // 监听滚动事件
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
      
      // 只有当用户手动滚动远离底部时才禁用自动滚动
      if (!isNearBottom && autoScroll) {
        setAutoScroll(false)
      } else if (isNearBottom && !autoScroll) {
        setAutoScroll(true)
      }
    }
    
    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [autoScroll])
  
  // 处理滚动事件
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
    
    if (isNearBottom !== autoScroll) {
      setAutoScroll(isNearBottom)
    }
  }
  
  // 格式化日期标题
  const formatDateHeader = (date: Date): string => {
    if (isToday(date)) {
      return '今天'
    } else if (isYesterday(date)) {
      return '昨天'
    } else {
      return format(date, 'yyyy年MM月dd日', { locale: zhCN })
    }
  }
  
  // 滚动到底部按钮
  const scrollToBottom = () => {
    setAutoScroll(true)
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  // 如果没有消息，显示提示
  if (messages.length === 0) {
    console.log('MessageList: 没有消息可显示')
    return (
      <div className="flex flex-col items-center justify-center h-96 bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-6xl mb-4">💬</div>
        <p className="text-secondary-500 text-center">选择一个场景并启动对话，消息将显示在这里</p>
        <p className="text-secondary-400 text-sm mt-2">您可以观察智能体之间的实时对话</p>
      </div>
    )
  }
  
  console.log('MessageList: 渲染消息列表，共', messages.length, '条消息')
  return (
    <div className="relative">
      <div 
        ref={containerRef}
        className="overflow-y-auto max-h-[600px] pr-2"
        onScroll={handleScroll}
      >
        {messageGroups.length === 0 ? (
          <div className="text-center py-8 text-secondary-500">
            暂无消息
          </div>
        ) : (
          <>
            {messageGroups.map((group, groupIndex) => (
              <div key={group.date.toISOString()}>
                <div className="flex items-center justify-center my-4">
                  <div className="bg-gray-200 text-secondary-600 text-xs px-2 py-1 rounded-full">
                    {formatDateHeader(group.date)}
                  </div>
                </div>
                
                <div className="space-y-4">
                  {group.messages.map(message => (
                    <MessageItem
                      key={message.id}
                      id={message.id}
                      sender={message.sender}
                      senderDisplayName={message.senderDisplayName}
                      content={message.content}
                      timestamp={message.timestamp}
                      isTyping={message.isTyping}
                      isQueued={message.isQueued}
                    />
                  ))}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      <AnimatePresence>
        {!autoScroll && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-4 right-4 bg-primary-500 text-white rounded-full p-2 shadow-md hover:bg-primary-600 transition-colors"
            onClick={scrollToBottom}
            title="滚动到最新消息"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}

export default MessageList 