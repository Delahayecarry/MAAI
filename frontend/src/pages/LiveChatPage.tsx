import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Tab } from '@headlessui/react'
import { useChatStore, Scenario } from '../store/chatStore'
import { useAgentStore } from '../store/agentStore'
import { apiService } from '../api/apiService'
import { useSSE } from '../hooks/useSSE'
import MessageList from '../components/MessageList'
import ScenarioSelector from '../components/ScenarioSelector'
import RelationshipGraph from '../components/RelationshipGraph'
import ChatStatistics from '../components/ChatStatistics'
import ConversationFlow from '../components/ConversationFlow'
import MessageTimeline from '../components/MessageTimeline'

const LiveChatPage = () => {
  const { messages, selectedScenario, selectScenario, isSimulationRunning, setSimulationRunning, useStreamingEffect, setUseStreamingEffect } = useChatStore()
  const { isConnected } = useSSE()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState(0)
  
  // 加载场景列表
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const scenarios = await apiService.getScenarios()
        useChatStore.getState().setScenarios(Array.isArray(scenarios) ? scenarios : [])
      } catch (err) {
        console.error('获取场景列表失败:', err)
        setError('获取场景列表失败，请检查后端服务是否正常运行')
      }
    }
    
    fetchScenarios()
  }, [])
  
  // 处理场景选择
  const handleScenarioSelect = (scenario: Scenario) => {
    console.log('选择场景:', scenario)
    selectScenario(scenario)
    setError(null)
  }
  
  // 检查SSE连接状态
  useEffect(() => {
    if (!isConnected && isSimulationRunning) {
      setError('SSE连接已断开，请刷新页面重新连接')
      console.error('SSE连接已断开，但模拟仍在运行')
    } else if (isConnected && error === 'SSE连接已断开，请刷新页面重新连接') {
      setError(null)
      console.log('SSE连接已恢复')
    }
    
    // 记录连接状态变化
    console.log('SSE连接状态变化:', isConnected ? '已连接' : '未连接')
  }, [isConnected, isSimulationRunning, error])
  
  // 启动模拟
  const handleStartSimulation = async () => {
    if (!selectedScenario) {
      setError('请先选择一个场景')
      return
    }
    
    setIsLoading(true)
    setError(null)
    
    try {
      console.log('启动模拟:', selectedScenario.id)
      const response = await apiService.startSimulation(selectedScenario.id)
      
      if (response.success) {
        console.log('模拟启动成功')
        setSimulationRunning(true)
        // 清空之前的消息
        useChatStore.getState().clearMessages()
        
        // 添加调试代码：每秒检查一次消息状态
        const checkMessages = setInterval(() => {
          const currentMessages = useChatStore.getState().messages;
          console.log('当前消息数量:', currentMessages.length);
          if (currentMessages.length > 0) {
            console.log('最新消息:', currentMessages[currentMessages.length - 1]);
            clearInterval(checkMessages);
          }
        }, 1000);
        
        // 30秒后清除定时器
        setTimeout(() => {
          clearInterval(checkMessages);
        }, 30000);
      } else {
        console.error('模拟启动失败:', response.message)
        setError(`模拟启动失败: ${response.message}`)
      }
    } catch (err) {
      console.error('启动模拟时出错:', err)
      setError('启动模拟时出错，请检查后端服务是否正常运行')
    } finally {
      setIsLoading(false)
    }
  }
  
  // 停止模拟
  const handleStopSimulation = async () => {
    setIsLoading(true)
    
    try {
      console.log('停止模拟')
      const response = await apiService.stopSimulation()
      
      if (response.success) {
        console.log('模拟停止成功')
        setSimulationRunning(false)
      } else {
        console.error('模拟停止失败:', response.message)
        setError(`模拟停止失败: ${response.message}`)
      }
    } catch (err) {
      console.error('停止模拟时出错:', err)
      setError('停止模拟时出错，请检查后端服务是否正常运行')
    } finally {
      setIsLoading(false)
    }
  }
  
  // 切换流式输出效果
  const toggleStreamingEffect = () => {
    setUseStreamingEffect(!useStreamingEffect)
  }
  
  return (
    <div>
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl font-bold text-secondary-800 mb-6"
      >
        实时智能体对话
      </motion.h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 左侧控制面板 */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1"
        >
          <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-6">
            <h2 className="text-lg font-medium text-secondary-800 mb-4">控制面板</h2>
            
            {!isSimulationRunning && (
              <ScenarioSelector onSelect={handleScenarioSelect} />
            )}
            
            <div className="flex flex-col space-y-3">
              {!isSimulationRunning ? (
                <button
                  onClick={handleStartSimulation}
                  disabled={isLoading || !selectedScenario}
                  className={`btn ${
                    isLoading || !selectedScenario
                      ? 'bg-gray-300 cursor-not-allowed'
                      : 'btn-primary'
                  }`}
                >
                  {isLoading ? '启动中...' : '启动对话'}
                </button>
              ) : (
                <button
                  onClick={handleStopSimulation}
                  disabled={isLoading}
                  className={`btn ${
                    isLoading ? 'bg-gray-300 cursor-not-allowed' : 'bg-red-500 text-white hover:bg-red-600'
                  }`}
                >
                  {isLoading ? '停止中...' : '停止对话'}
                </button>
              )}
              
              <div className="flex items-center mt-2">
                <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-secondary-600">
                  {isConnected ? 'SSE已连接' : 'SSE未连接'}
                </span>
              </div>
              
              <div className="flex items-center justify-between mt-2 py-2 border-t border-gray-100">
                <span className="text-sm text-secondary-600">流式输出效果</span>
                <button
                  onClick={toggleStreamingEffect}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                    useStreamingEffect ? 'bg-primary-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      useStreamingEffect ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {isSimulationRunning && (
                <div className="mt-4">
                  <h3 className="text-md font-medium text-secondary-800 mb-2">当前场景</h3>
                  <div className="bg-primary-50 border border-primary-100 rounded-md p-3">
                    <p className="font-medium text-primary-700">{selectedScenario?.name}</p>
                    <p className="text-sm text-primary-600 mt-1">{selectedScenario?.description}</p>
                  </div>
                </div>
              )}
              
              {messages.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-md font-medium text-secondary-800 mb-2">对话统计</h3>
                  <p className="text-sm text-secondary-600">消息总数: {messages.length}</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
        
        {/* 右侧内容区 */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3"
        >
          <Tab.Group selectedIndex={activeTab} onChange={setActiveTab}>
            <Tab.List className="flex space-x-1 rounded-xl bg-primary-50 p-1 mb-4">
              <Tab
                className={({ selected }) =>
                  `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
                  ${selected
                    ? 'bg-white shadow text-primary-700'
                    : 'text-primary-500 hover:bg-white/[0.12] hover:text-primary-600'
                  }`
                }
              >
                对话内容
              </Tab>
              <Tab
                className={({ selected }) =>
                  `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
                  ${selected
                    ? 'bg-white shadow text-primary-700'
                    : 'text-primary-500 hover:bg-white/[0.12] hover:text-primary-600'
                  }`
                }
              >
                可视化分析
              </Tab>
            </Tab.List>
            <Tab.Panels>
              {/* 对话内容面板 */}
              <Tab.Panel>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <h2 className="text-lg font-medium text-secondary-800 mb-4">对话内容</h2>
                  
                  {messages.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-secondary-500 mb-4">
                        {isSimulationRunning 
                          ? '等待智能体开始对话...' 
                          : '请选择一个场景并启动对话'}
                      </p>
                      {!isSimulationRunning && (
                        <button
                          onClick={handleStartSimulation}
                          disabled={isLoading || !selectedScenario}
                          className={`btn ${
                            isLoading || !selectedScenario
                              ? 'bg-gray-300 cursor-not-allowed'
                              : 'btn-primary'
                          }`}
                        >
                          {isLoading ? '启动中...' : '启动对话'}
                        </button>
                      )}
                    </div>
                  ) : (
                    <MessageList />
                  )}
                </div>
              </Tab.Panel>
              
              {/* 可视化分析面板 */}
              <Tab.Panel>
                <div className="space-y-6">
                  {/* 统计信息 */}
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <h2 className="text-lg font-medium text-secondary-800 mb-4">对话统计</h2>
                    <ChatStatistics />
                  </div>
                  
                  {/* 关系网络 */}
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <h2 className="text-lg font-medium text-secondary-800 mb-4">智能体关系网络</h2>
                    <p className="text-sm text-secondary-500 mb-4">
                      此图展示了智能体之间的关系网络，支持缩放和拖动。节点大小表示消息数量，连线粗细表示交互频率。
                    </p>
                    <div className="h-[500px] border border-gray-100 rounded-lg overflow-hidden">
                      <RelationshipGraph />
                    </div>
                  </div>
                  
                  {/* 对话流 */}
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <h2 className="text-lg font-medium text-secondary-800 mb-4">对话流分析</h2>
                    <ConversationFlow />
                  </div>
                  
                  {/* 消息时间线 */}
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <h2 className="text-lg font-medium text-secondary-800 mb-4">消息时间线</h2>
                    <MessageTimeline />
                  </div>
                </div>
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </motion.div>
      </div>
    </div>
  )
}

export default LiveChatPage 