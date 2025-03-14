import { create } from 'zustand'
import { Agent } from './agentStore'

export interface Message {
  id: string
  sender: string
  senderDisplayName: string
  content: string
  timestamp: string
  isTyping?: boolean
  isQueued?: boolean
}

export interface Scenario {
  id: string
  name: string
  description: string
}

interface ChatState {
  messages: Message[]
  scenarios: Scenario[]
  selectedScenario: Scenario | null
  isSimulationRunning: boolean
  useStreamingEffect: boolean
  typingMessageId: string | null
  messageQueue: string[]
  addMessage: (message: Message) => void
  clearMessages: () => void
  setScenarios: (scenarios: Scenario[]) => void
  selectScenario: (scenario: Scenario | null) => void
  setSimulationRunning: (isRunning: boolean) => void
  setUseStreamingEffect: (useEffect: boolean) => void
  setMessageTypingState: (messageId: string, isTyping: boolean) => void
  dequeueNextMessage: () => string | null
  getMessageById: (messageId: string) => Message | undefined
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  scenarios: [
    {
      id: "team_meeting",
      name: "团队会议",
      description: "团队成员讨论项目进展和问题"
    },
    {
      id: "technical_discussion",
      name: "技术讨论",
      description: "讨论项目技术栈选择"
    },
    {
      id: "design_review",
      name: "设计评审",
      description: "团队评审设计方案"
    },
    {
      id: "conflict_resolution",
      name: "冲突解决",
      description: "解决团队成员之间的冲突"
    },
    {
      id: "casual_chat",
      name: "休闲聊天",
      description: "团队成员的轻松对话"
    }
  ],
  selectedScenario: null,
  isSimulationRunning: false,
  useStreamingEffect: true,
  typingMessageId: null,
  messageQueue: [],
  
  addMessage: (message) => {
    console.log('Store: 添加消息', message)
    
    // 检查消息是否已存在
    const currentMessages = get().messages
    if (currentMessages.some(m => m.id === message.id)) {
      console.log('Store: 消息已存在，跳过添加', message.id)
      return
    }
    
    const { useStreamingEffect, typingMessageId, messageQueue } = get()
    
    // 如果启用了流式效果
    if (useStreamingEffect) {
      // 如果当前没有消息正在输入，则设置这条消息为正在输入状态
      if (!typingMessageId) {
        console.log('Store: 设置消息为正在输入状态', message.id)
        set((state) => {
          const newMessages = [...state.messages, { ...message, isTyping: true }]
          return { 
            messages: newMessages, 
            typingMessageId: message.id 
          }
        })
      } else {
        // 否则，将消息添加到队列中，并标记为排队状态
        console.log('Store: 将消息添加到队列', message.id)
        set((state) => {
          const newQueue = [...state.messageQueue, message.id]
          const newMessages = [...state.messages, { ...message, isQueued: true }]
          return { 
            messages: newMessages, 
            messageQueue: newQueue 
          }
        })
      }
    } else {
      // 如果没有启用流式效果，直接添加消息
      set((state) => {
        const newMessages = [...state.messages, message]
        return { messages: newMessages }
      })
    }
    
    console.log('Store: 消息已添加，新长度:', get().messages.length)
  },
  
  clearMessages: () => {
    console.log('Store: 清空消息')
    set({ 
      messages: [],
      typingMessageId: null,
      messageQueue: []
    })
  },
  
  setScenarios: (scenarios) => {
    console.log('Store: 设置场景列表', scenarios)
    set({ scenarios })
  },
  
  selectScenario: (scenario) => {
    console.log('Store: 选择场景', scenario)
    set({ selectedScenario: scenario })
  },
  
  setSimulationRunning: (isRunning) => {
    console.log('Store: 设置模拟状态', isRunning)
    set({ isSimulationRunning: isRunning })
  },
  
  setUseStreamingEffect: (useEffect) => {
    console.log('Store: 设置流式输出效果', useEffect)
    
    // 如果关闭流式效果，清除所有排队和输入状态
    if (!useEffect) {
      set((state) => {
        const updatedMessages = state.messages.map(msg => ({
          ...msg,
          isTyping: false,
          isQueued: false
        }))
        return { 
          useStreamingEffect: useEffect,
          messages: updatedMessages,
          typingMessageId: null,
          messageQueue: []
        }
      })
    } else {
      set({ useStreamingEffect: useEffect })
    }
  },
  
  setMessageTypingState: (messageId, isTyping) => {
    console.log(`Store: 设置消息 ${messageId} 的输入状态为 ${isTyping}`)
    
    // 获取当前状态
    const { messages, typingMessageId, messageQueue } = get()
    
    // 如果消息不存在，记录错误并返回
    const messageIndex = messages.findIndex(msg => msg.id === messageId)
    if (messageIndex === -1) {
      console.error(`Store: 找不到消息 ${messageId}`)
      return
    }
    
    // 更新消息的输入状态
    const updatedMessages = [...messages]
    updatedMessages[messageIndex] = { 
      ...updatedMessages[messageIndex], 
      isTyping: isTyping, 
      isQueued: false 
    }
    
    // 如果消息完成输入，清除当前输入消息ID
    const newTypingMessageId = isTyping ? messageId : null
    
    // 更新状态
    set({ 
      messages: updatedMessages,
      typingMessageId: newTypingMessageId
    })
    
    // 如果消息完成输入，且队列中有消息，处理下一条消息
    if (!isTyping && messageQueue.length > 0) {
      setTimeout(() => {
        const nextMessageId = get().dequeueNextMessage()
        if (nextMessageId) {
          console.log('Store: 处理队列中的下一条消息', nextMessageId)
          
          // 获取最新状态
          const currentMessages = get().messages
          const nextMessageIndex = currentMessages.findIndex(msg => msg.id === nextMessageId)
          
          if (nextMessageIndex !== -1) {
            const updatedMessages = [...currentMessages]
            updatedMessages[nextMessageIndex] = { 
              ...updatedMessages[nextMessageIndex], 
              isTyping: true, 
              isQueued: false 
            }
            
            set({ 
              messages: updatedMessages,
              typingMessageId: nextMessageId
            })
          }
        }
      }, 500) // 添加延迟，确保前一条消息的动画效果完成
    }
  },
  
  dequeueNextMessage: () => {
    const { messageQueue } = get()
    if (messageQueue.length === 0) return null
    
    // 获取队列中的第一条消息
    const nextMessageId = messageQueue[0]
    
    // 更新队列
    set((state) => ({
      messageQueue: state.messageQueue.slice(1)
    }))
    
    return nextMessageId
  },
  
  getMessageById: (messageId) => {
    return get().messages.find(msg => msg.id === messageId)
  }
})) 