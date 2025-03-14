import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import AgentCard from '../components/AgentCard'

const HomePage = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }
  
  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  }

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-12"
      >
        <h1 className="text-3xl font-bold text-primary-600 mb-4">欢迎使用多智能体交互系统</h1>
        <p className="text-lg text-secondary-600 max-w-3xl mx-auto">
          这是一个基于AutoGen框架的多智能体交互系统，用于模拟团队协作场景。
          通过实时对话和可视化，您可以观察智能体之间的交互过程。
        </p>
      </motion.div>
      
      <div className="mb-12">
        <motion.h2 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-2xl font-semibold text-secondary-800 mb-6"
        >
          系统特点
        </motion.h2>
        
        <motion.ul
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          <motion.li variants={itemVariants} className="card">
            <h3 className="text-lg font-medium text-primary-600 mb-2">多种预定义场景</h3>
            <p className="text-secondary-600">支持多种团队协作场景，如团队会议、代码审查、产品设计等</p>
          </motion.li>
          <motion.li variants={itemVariants} className="card">
            <h3 className="text-lg font-medium text-primary-600 mb-2">实时对话展示</h3>
            <p className="text-secondary-600">通过SSE技术实时展示智能体之间的对话内容，无需刷新页面</p>
          </motion.li>
          <motion.li variants={itemVariants} className="card">
            <h3 className="text-lg font-medium text-primary-600 mb-2">历史记录查看</h3>
            <p className="text-secondary-600">保存并查看历史对话记录，方便回顾和分析</p>
          </motion.li>
          <motion.li variants={itemVariants} className="card">
            <h3 className="text-lg font-medium text-primary-600 mb-2">关系网络可视化</h3>
            <p className="text-secondary-600">使用D3力导向图可视化智能体之间的关系网络</p>
          </motion.li>
        </motion.ul>
      </div>
      
      <div className="mb-12">
        <motion.h2 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-2xl font-semibold text-secondary-800 mb-6"
        >
          系统中的智能体
        </motion.h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <AgentCard 
            name="Manager" 
            displayName="经理" 
            description="团队领导，负责协调和决策" 
            emoji="👨‍💼" 
          />
          <AgentCard 
            name="SeniorDev" 
            displayName="资深开发" 
            description="经验丰富的开发人员" 
            emoji="👨‍💻" 
          />
          <AgentCard 
            name="JuniorDev" 
            displayName="初级开发" 
            description="新加入的开发人员" 
            emoji="🧑‍💻" 
          />
          <AgentCard 
            name="Designer" 
            displayName="设计师" 
            description="负责用户界面和体验设计" 
            emoji="👩‍🎨" 
          />
        </div>
      </div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="text-center"
      >
        <Link to="/live-chat" className="btn btn-primary">
          开始体验实时对话
        </Link>
      </motion.div>
    </div>
  )
}

export default HomePage 