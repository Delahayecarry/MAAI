import { useEffect, useRef, useState } from 'react'
import { sseService } from '../api/sseService'

export const useSSE = () => {
  const [connected, setConnected] = useState(false)
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null)
  const connectionCheckIntervalRef = useRef<NodeJS.Timeout | null>(null)
  
  useEffect(() => {
    console.log('useSSE hook: 组件挂载，准备连接SSE')
    
    // 连接SSE
    sseService.connect()
    
    // 检查连接状态
    const checkConnection = () => {
      const isConnected = sseService.isConnected()
      console.log('SSE连接状态检查:', isConnected)
      setConnected(isConnected)
      
      // 如果未连接，尝试重连
      if (!isConnected) {
        console.log('SSE未连接，尝试重连')
        sseService.connect()
      }
    }
    
    // 立即检查一次
    checkConnection()
    
    // 设置定期检查
    connectionCheckIntervalRef.current = setInterval(checkConnection, 5000)
    
    // 组件卸载时断开连接
    return () => {
      console.log('useSSE hook: 组件卸载，断开SSE连接')
      if (connectionCheckIntervalRef.current) {
        clearInterval(connectionCheckIntervalRef.current)
        connectionCheckIntervalRef.current = null
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current)
        reconnectTimerRef.current = null
      }
      sseService.disconnect()
      setConnected(false)
    }
  }, [])
  
  const connect = () => {
    console.log('useSSE hook: 手动连接SSE')
    sseService.connect()
    // 不要立即设置连接状态，等待实际连接成功
    setTimeout(() => {
      setConnected(sseService.isConnected())
    }, 1000)
  }
  
  const disconnect = () => {
    console.log('useSSE hook: 手动断开SSE连接')
    sseService.disconnect()
    setConnected(false)
  }
  
  return {
    connect,
    disconnect,
    isConnected: connected
  }
} 