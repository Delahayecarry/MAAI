import { create } from 'zustand'

export interface Agent {
  name: string
  displayName: string
  traits?: string
  relationships?: Record<string, string>
  emoji: string
}

interface AgentState {
  agents: Agent[]
  selectedAgent: Agent | null
  setAgents: (agents: Agent[]) => void
  selectAgent: (agent: Agent | null) => void
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [
    {
      name: "Manager",
      displayName: "经理",
      traits: "团队领导，负责协调和决策",
      relationships: { "资深开发": "赏识", "初级开发": "指导", "设计师": "合作" },
      emoji: "👨‍💼"
    },
    {
      name: "SeniorDev",
      displayName: "资深开发",
      traits: "经验丰富、效率高、技术精湛",
      relationships: { "经理": "受到赏识", "初级开发": "有些不耐烦", "设计师": "配合良好" },
      emoji: "👨‍💻"
    },
    {
      name: "JuniorDev",
      displayName: "初级开发",
      traits: "有创意但经验不足、工作效率低",
      relationships: { "经理": "感到压力", "资深开发": "有些敬畏", "设计师": "友好" },
      emoji: "🧑‍💻"
    },
    {
      name: "Designer",
      displayName: "设计师",
      traits: "创意丰富、注重细节、有时固执己见",
      relationships: { "经理": "关系中立", "资深开发": "配合良好", "初级开发": "友好" },
      emoji: "👩‍🎨"
    }
  ],
  selectedAgent: null,
  setAgents: (agents) => set({ agents }),
  selectAgent: (agent) => set({ selectedAgent: agent })
})) 