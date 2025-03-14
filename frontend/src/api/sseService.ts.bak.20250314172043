import { useChatStore } from '../store/chatStore'

export class SSEService {
  private reconnectAttempts = 0
  private eventSource: EventSource | null = null
  
  // 连接到SSE事件流
  connect(): void {
    if (this.eventSource) {
      this.disconnect()
    }
    
    console.log('正在连接SSE事件流...')
    this.eventSource = new EventSource('/api/events')
    
    // 处理连接打开
    this.eventSource.onopen = () => {
      console.log('SSE连接已建立')
      this.resetReconnectAttempts()
    }
    
    // 处理消息事件
    this.eventSource.addEventListener('message', this.handleMessage)
    
    // 处理智能体消息事件
    this.eventSource.addEventListener('agent_message', this.handleAgentMessage)
    
    // 处理模拟状态变更事件
    this.eventSource.addEventListener('simulation_status', this.handleSimulationStatus)
    
    // 处理错误
    this.eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      
      // 检查错误类型
      if (this.eventSource && this.eventSource.readyState === EventSource.CLOSED) {
        console.log('SSE连接已关闭，尝试重新连接')
        this.reconnect()
      } else if (this.eventSource && this.eventSource.readyState === EventSource.CONNECTING) {
        console.log('SSE正在尝试连接，等待连接结果')
        // 等待连接结果，不立即重连
      } else {
        console.log('SSE连接出现未知错误，尝试重新连接')
        this.reconnect()
      }
    }
  }
  
  // 断开连接
  disconnect(): void {
    if (this.eventSource) {
      console.log('正在断开SSE连接...')
      this.eventSource.removeEventListener('message', this.handleMessage)
      this.eventSource.removeEventListener('agent_message', this.handleAgentMessage)
      this.eventSource.removeEventListener('simulation_status', this.handleSimulationStatus)
      this.eventSource.close()
      this.eventSource = null
      console.log('SSE连接已关闭')
    }
  }
  
  // 重新连接
  private reconnect(): void {
    // 如果已经有连接，先断开
    if (this.eventSource) {
      this.disconnect()
    }
    
    // 使用指数退避策略进行重连
    const backoffTime = Math.min(3000 * Math.pow(2, this.reconnectAttempts), 30000)
    this.reconnectAttempts++
    
    console.log(`尝试第 ${this.reconnectAttempts} 次重新连接SSE，等待 ${backoffTime/1000} 秒...`)
    
    setTimeout(() => {
      console.log('正在重新连接SSE...')
      this.connect()
    }, backoffTime)
  }
  
  // 重置重连尝试次数
  private resetReconnectAttempts(): void {
    this.reconnectAttempts = 0
  }
  
  // 处理普通消息
  private handleMessage = (event: MessageEvent): void => {
    try {
      console.log('收到普通SSE消息:', event.data)
      const data = JSON.parse(event.data)
      console.log('解析后的SSE消息:', data)
    } catch (error) {
      console.error('解析SSE消息失败:', error)
    }
  }
  
  // 处理智能体消息
  private handleAgentMessage = (event: MessageEvent): void => {
    try {
      console.log('收到智能体消息事件:', event.data)
      console.log('事件类型:', event.type)
      
      // 检查数据是否为空
      if (!event.data) {
        console.error('收到空的智能体消息数据')
        return
      }
      
      // 尝试解析JSON
      const message = JSON.parse(event.data)
      console.log('解析后的智能体消息:', message)
      
      // 检查消息格式
      if (!message.sender || !message.content) {
        console.error('消息格式不正确，缺少必要字段:', message)
        return
      }
      
      // 检查内容是否为乱码
      const content = message.content
      if (content && typeof content === 'string') {
        // 如果内容包含大量乱码字符，可能是编码问题
        const invalidCharsCount = (content.match(/\ufffd/g) || []).length
        if (invalidCharsCount > content.length * 0.3) {
          console.warn('消息内容可能包含乱码，尝试修复:', content)
          // 这里可以尝试修复，但目前先记录日志
        }
      }
      
      const { addMessage } = useChatStore.getState()
      const currentMessages = useChatStore.getState().messages
      console.log('当前消息列表长度:', currentMessages.length)
      console.log('当前消息列表:', currentMessages)
      
      // 检查是否已存在相同ID的消息
      if (message.id && currentMessages.some(m => m.id === message.id)) {
        console.log('消息已存在，跳过添加:', message.id)
        return
      }
      
      const newMessage = {
        id: message.id || Date.now().toString(),
        sender: message.sender,
        senderDisplayName: message.sender_display_name || message.sender,
        content: message.content,
        timestamp: message.timestamp || new Date().toISOString()
      }
      
      console.log('添加新消息:', newMessage)
      addMessage(newMessage)
      // 注意: 如果消息顺序有问题，可以考虑在chatStore中添加排序逻辑:
      // messages.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      
      // 验证消息是否已添加
      setTimeout(() => {
        const updatedMessages = useChatStore.getState().messages
        console.log('消息已添加，新长度:', updatedMessages.length)
        if (updatedMessages.length > 0) {
          console.log('最新消息:', updatedMessages[updatedMessages.length - 1])
        }
      }, 0)
    } catch (error) {
      console.error('处理智能体消息失败:', error, '原始数据:', event.data)
    }
  }
  
  // 处理模拟状态变更
  private handleSimulationStatus = (event: MessageEvent): void => {
    try {
      console.log('收到模拟状态变更事件:', event.data)
      const data = JSON.parse(event.data)
      console.log('解析后的模拟状态:', data)
      
      const { setSimulationRunning } = useChatStore.getState()
      console.log('设置模拟状态:', data.is_running)
      
      setSimulationRunning(data.is_running)
      
      if (!data.is_running) {
        console.log('模拟已结束')
      }
    } catch (error) {
      console.error('处理模拟状态变更失败:', error, '原始数据:', event.data)
    }
  }
}

// 创建单例实例
export const sseService = new SSEService() 