import { motion } from 'framer-motion'

interface AgentCardProps {
  name: string
  displayName: string
  description: string
  emoji: string
}

const AgentCard = ({ name, displayName, description, emoji }: AgentCardProps) => {
  return (
    <motion.div 
      whileHover={{ y: -5, boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)' }}
      className="card overflow-hidden"
    >
      <div className="flex items-center mb-3">
        <div className="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-xl">
          {emoji}
        </div>
        <div className="ml-3">
          <h3 className="text-lg font-medium text-secondary-800">{displayName}</h3>
          <p className="text-sm text-secondary-500">{name}</p>
        </div>
      </div>
      <p className="text-secondary-600">{description}</p>
    </motion.div>
  )
}

export default AgentCard 