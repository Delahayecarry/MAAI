import { motion } from 'framer-motion'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { useAgentStore } from '../store/agentStore'
import { useChatStore } from '../store/chatStore'
import { useEffect, useState } from 'react'

interface MessageItemProps {
  id: string
  sender: string
  senderDisplayName: string
  content: string
  timestamp: string
  isTyping?: boolean
  isQueued?: boolean
}

const MessageItem = ({ id, sender, senderDisplayName, content, timestamp, isTyping: propIsTyping, isQueued }: MessageItemProps) => {
  const { agents } = useAgentStore()
  const { useStreamingEffect, setMessageTypingState } = useChatStore()
  const [isSystem, setIsSystem] = useState(false)
  const [isError, setIsError] = useState(false)
  const [displayedContent, setDisplayedContent] = useState('')
  const [typingIndex, setTypingIndex] = useState(0)
  
  // 检查消息类型
  useEffect(() => {
    setIsSystem(sender === 'System')
    setIsError(content.toLowerCase().includes('error') || content.includes('错误') || content.includes('失败'))
  }, [sender, content])
  
  // 处理打字状态变化
  useEffect(() => {
    if (propIsTyping === true) {
      // 开始打字
      setTypingIndex(0)
      setDisplayedContent('')
    } else if (propIsTyping === false) {
      // 结束打字
      setDisplayedContent(content)
      setTypingIndex(content.length)
    }
  }, [propIsTyping, id, content])
  
  // 流式输出效果
  useEffect(() => {
    // 如果不是打字状态或不使用流式效果，不处理
    if (!propIsTyping || !useStreamingEffect) return
    
    // 如果已经显示完全部内容，结束打字
    if (typingIndex >= content.length) {
      setMessageTypingState(id, false)
      return
    }
    
    // 设置定时器，逐字显示内容
    const timer = setTimeout(() => {
      const nextChar = content[typingIndex]
      
      // 更新显示内容
      setDisplayedContent(prev => prev + nextChar)
      setTypingIndex(prev => prev + 1)
    }, getDelayForChar(content[typingIndex]))
    
    // 清理函数
    return () => clearTimeout(timer)
  }, [propIsTyping, useStreamingEffect, typingIndex, content, id, setMessageTypingState])
  
  // 根据字符类型获取延迟时间
  const getDelayForChar = (char: string): number => {
    if (!char) return 30
    
    if (['.', '!', '?', '。', '！', '？'].includes(char)) {
      return 300 // 句子结束后较长停顿
    } else if ([',', ';', '，', '；', '、'].includes(char)) {
      return 150 // 逗号等标点后中等停顿
    } else if (['\n', '\r'].includes(char)) {
      return 400 // 换行后更长停顿
    }
    
    return 30 // 基础延迟30ms
  }
  
  // 跳过打字
  const skipTyping = () => {
    setDisplayedContent(content)
    setTypingIndex(content.length)
    setMessageTypingState(id, false)
  }
  
  // 重新开始打字
  const restartTyping = () => {
    setTypingIndex(0)
    setDisplayedContent('')
    setMessageTypingState(id, true)
  }
  
  // 查找对应的智能体
  const agent = agents.find(a => a.name === sender)
  const emoji = agent?.emoji || (sender === 'System' ? '🔧' : '🤖')
  
  // 格式化时间戳
  let formattedTime = ''
  try {
    formattedTime = format(new Date(timestamp), 'HH:mm:ss', { locale: zhCN })
  } catch (error) {
    console.error('格式化时间戳失败:', error, timestamp)
    formattedTime = timestamp
  }
  
  // 根据发送者设置不同的样式
  const getBubbleStyle = () => {
    if (isSystem) {
      return 'bg-gray-100 border border-gray-200'
    } else if (isError) {
      return 'bg-red-50 border border-red-200 text-red-700'
    } else if (isQueued) {
      return 'bg-gray-50 border border-gray-200 opacity-60'
    } else {
      return 'bg-white border border-gray-200 shadow-sm'
    }
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`mb-4 group ${isQueued ? 'opacity-60' : ''}`}
      data-message-id={id}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-xl relative">
          {emoji}
          {isSystem && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full border-2 border-white"></span>
          )}
          {isError && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-white"></span>
          )}
          {isQueued && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-500 rounded-full border-2 border-white flex items-center justify-center">
              <span className="text-[8px] text-white font-bold">⏱</span>
            </span>
          )}
        </div>
        <div className={`ml-3 rounded-lg p-3 max-w-3xl ${getBubbleStyle()}`}>
          <div className="flex items-baseline mb-1">
            <span className={`font-medium ${isSystem ? 'text-blue-600' : isError ? 'text-red-600' : 'text-secondary-800'}`}>
              {senderDisplayName}
            </span>
            <span className="ml-2 text-xs text-secondary-400">{formattedTime}</span>
            {isQueued && (
              <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-1 rounded">排队中</span>
            )}
          </div>
          <div className={`whitespace-pre-wrap ${isSystem ? 'text-secondary-600' : isError ? 'text-red-700' : 'text-secondary-700'}`}>
            {displayedContent}
            {propIsTyping && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ repeat: Infinity, duration: 0.5, repeatType: "reverse" }}
                className="inline-block ml-1"
              >
                ▌
              </motion.span>
            )}
          </div>
        </div>
      </div>
      
      <div className="mt-1 ml-14 flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          className="text-xs text-secondary-500 hover:text-secondary-700 mr-3"
          onClick={() => {
            navigator.clipboard.writeText(content)
              .then(() => alert('消息已复制到剪贴板'))
              .catch(err => console.error('复制失败:', err))
          }}
        >
          复制
        </button>
        {!isQueued && (
          <button 
            className="text-xs text-secondary-500 hover:text-secondary-700 mr-3"
            onClick={() => {
              // 如果正在打字，立即显示全部内容
              if (propIsTyping) {
                skipTyping()
              } else {
                // 如果已经显示完毕，重新开始打字效果
                restartTyping()
              }
            }}
          >
            {propIsTyping ? '跳过' : '重放'}
          </button>
        )}
        <span className="text-xs text-secondary-400">ID: {id.substring(0, 8)}...</span>
      </div>
    </motion.div>
  )
}

export default MessageItem 