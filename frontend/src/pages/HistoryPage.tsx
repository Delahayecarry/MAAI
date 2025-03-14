import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { useChatStore } from '../store/chatStore'
import MessageItem from '../components/MessageItem'
import { apiService } from '../api/apiService'

interface HistoryItem {
  id: string
  timestamp: string
  scenario: string
}

const HistoryPage = () => {
  const [historyList, setHistoryList] = useState<HistoryItem[]>([])
  const [selectedHistory, setSelectedHistory] = useState<string | null>(null)
  const [historyMessages, setHistoryMessages] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // 加载历史记录列表
  useEffect(() => {
    const fetchHistoryList = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const data = await apiService.getHistoryList()
        setHistoryList(data)
      } catch (err) {
        setError('获取历史记录列表失败')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchHistoryList()
  }, [])
  
  // 加载特定历史记录
  const handleHistorySelect = async (id: string) => {
    setIsLoading(true)
    setError(null)
    setSelectedHistory(id)
    
    try {
      const data = await apiService.getHistoryById(id)
      setHistoryMessages(data)
    } catch (err) {
      setError('获取历史记录详情失败')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }
  
  // 格式化时间戳
  const formatTimestamp = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'yyyy年MM月dd日 HH:mm:ss', { locale: zhCN })
    } catch (err) {
      return timestamp
    }
  }
  
  return (
    <div>
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl font-bold text-secondary-800 mb-6"
      >
        历史对话记录
      </motion.h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg border border-gray-200 p-4"
        >
          <h2 className="text-lg font-medium text-secondary-800 mb-4">对话记录列表</h2>
          
          {isLoading && historyList.length === 0 ? (
            <p className="text-secondary-500">加载中...</p>
          ) : historyList.length === 0 ? (
            <p className="text-secondary-500">暂无历史对话记录</p>
          ) : (
            <ul className="space-y-2">
              {historyList.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => handleHistorySelect(item.id)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      selectedHistory === item.id
                        ? 'bg-primary-50 text-primary-600'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium">{item.scenario}</div>
                    <div className="text-sm text-secondary-500">
                      {formatTimestamp(item.timestamp)}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h2 className="text-lg font-medium text-secondary-800 mb-4">对话内容</h2>
            
            {isLoading && selectedHistory ? (
              <p className="text-secondary-500">加载中...</p>
            ) : !selectedHistory ? (
              <p className="text-secondary-500">请从左侧选择一条历史记录</p>
            ) : historyMessages.length === 0 ? (
              <p className="text-secondary-500">该对话记录为空</p>
            ) : (
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {historyMessages.map((message) => (
                  <MessageItem
                    key={message.id}
                    id={message.id}
                    sender={message.sender}
                    senderDisplayName={message.sender_display_name}
                    content={message.content}
                    timestamp={message.timestamp}
                  />
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default HistoryPage 