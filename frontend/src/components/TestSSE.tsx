import { useState, useEffect } from 'react'
import { sseService } from '../api/sseService'
import { useChatStore } from '../store/chatStore'

const TestSSE = () => {
  const { messages } = useChatStore()
  const [connected, setConnected] = useState(false)
  const [testMessage, setTestMessage] = useState('')
  
  // 连接SSE
  useEffect(() => {
    console.log('TestSSE: 组件挂载，连接SSE')
    sseService.connect()
    setConnected(true)
    
    return () => {
      console.log('TestSSE: 组件卸载，断开SSE连接')
      sseService.disconnect()
      setConnected(false)
    }
  }, [])
  
  // 发送测试消息
  const sendTestMessage = () => {
    if (!testMessage.trim()) return
    
    const newMessage = {
      id: Date.now().toString(),
      sender: 'TestUser',
      senderDisplayName: '测试用户',
      content: testMessage,
      timestamp: new Date().toISOString()
    }
    
    console.log('TestSSE: 发送测试消息', newMessage)
    useChatStore.getState().addMessage(newMessage)
    setTestMessage('')
  }
  
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <h3 className="text-lg font-medium text-secondary-800 mb-3">SSE连接测试</h3>
      
      <div className="mb-4">
        <div className="flex items-center mb-2">
          <div className={`w-3 h-3 rounded-full mr-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span>{connected ? 'SSE已连接' : 'SSE未连接'}</span>
        </div>
        
        <button 
          onClick={() => connected ? sseService.disconnect() : sseService.connect()}
          className="btn btn-secondary mr-2"
        >
          {connected ? '断开连接' : '连接'}
        </button>
        
        <button 
          onClick={() => {
            useChatStore.getState().clearMessages()
            console.log('TestSSE: 清空消息')
          }}
          className="btn btn-secondary"
        >
          清空消息
        </button>
      </div>
      
      <div className="mb-4">
        <div className="flex">
          <input
            type="text"
            value={testMessage}
            onChange={(e) => setTestMessage(e.target.value)}
            placeholder="输入测试消息"
            className="input flex-1 mr-2"
          />
          <button 
            onClick={sendTestMessage}
            className="btn btn-primary"
          >
            发送
          </button>
        </div>
      </div>
      
      <div>
        <h4 className="font-medium mb-2">当前消息 ({messages.length})</h4>
        <div className="bg-gray-50 p-3 rounded-md max-h-40 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-secondary-500">暂无消息</p>
          ) : (
            <ul className="space-y-2">
              {messages.map((msg) => (
                <li key={msg.id} className="text-sm">
                  <span className="font-medium">{msg.senderDisplayName}:</span> {msg.content}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default TestSSE 