import axios from 'axios'
import { Scenario } from '../store/chatStore'

const API_URL = '/api'

export const apiService = {
  // 获取所有场景
  getScenarios: async (): Promise<Scenario[]> => {
    try {
      console.log('API: 获取场景列表')
      const response = await axios.get(`${API_URL}/scenarios`)
      console.log('API: 获取场景列表成功', response.data)
      return response.data
    } catch (error) {
      console.error('API: 获取场景失败:', error)
      throw error
    }
  },
  
  // 启动模拟
  startSimulation: async (scenarioId: string): Promise<{ success: boolean, message: string }> => {
    try {
      console.log('API: 启动模拟', scenarioId)
      const response = await axios.post(`${API_URL}/simulation/start`, { scenario_id: scenarioId })
      console.log('API: 启动模拟响应', response.data)
      return response.data
    } catch (error) {
      console.error('API: 启动模拟失败:', error)
      throw error
    }
  },
  
  // 停止模拟
  stopSimulation: async (): Promise<{ success: boolean, message: string }> => {
    try {
      console.log('API: 停止模拟')
      const response = await axios.post(`${API_URL}/simulation/stop`)
      console.log('API: 停止模拟响应', response.data)
      return response.data
    } catch (error) {
      console.error('API: 停止模拟失败:', error)
      throw error
    }
  },
  
  // 获取历史对话列表
  getHistoryList: async (): Promise<{ id: string, timestamp: string, scenario: string }[]> => {
    try {
      console.log('API: 获取历史对话列表')
      const response = await axios.get(`${API_URL}/history`)
      console.log('API: 获取历史对话列表成功', response.data)
      return response.data
    } catch (error) {
      console.error('API: 获取历史对话列表失败:', error)
      throw error
    }
  },
  
  // 获取特定历史对话
  getHistoryById: async (id: string): Promise<any> => {
    try {
      console.log('API: 获取历史对话', id)
      const response = await axios.get(`${API_URL}/history/${id}`)
      console.log('API: 获取历史对话成功', response.data)
      return response.data
    } catch (error) {
      console.error('API: 获取历史对话失败:', error)
      throw error
    }
  }
} 