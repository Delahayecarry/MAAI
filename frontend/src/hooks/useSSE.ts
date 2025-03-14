import { useEffect, useRef, useState } from 'react'
import { sseService } from '../api/sseService'

export const useSSE = () => {
  const [connected, setConnected] = useState(false)
  
  useEffect(() => {
    console.log('useSSE hook: 组件挂载，准备连接SSE')
    
    // 连接SSE
    sseService.connect()
    setConnected(true)
    
    // 组件卸载时断开连接
    return () => {
      console.log('useSSE hook: 组件卸载，断开SSE连接')
      sseService.disconnect()
      setConnected(false)
    }
  }, [])
  
  const connect = () => {
    console.log('useSSE hook: 手动连接SSE')
    sseService.connect()
    setConnected(true)
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