import { RadioGroup } from '@headlessui/react'
import { motion } from 'framer-motion'
import { useChatStore, Scenario } from '../store/chatStore'

interface ScenarioSelectorProps {
  onSelect: (scenario: Scenario) => void
}

const ScenarioSelector = ({ onSelect }: ScenarioSelectorProps) => {
  const { scenarios, selectedScenario, selectScenario } = useChatStore()
  
  const handleSelect = (scenario: Scenario) => {
    selectScenario(scenario)
    onSelect(scenario)
  }
  
  return (
    <div className="mb-6">
      <h3 className="text-lg font-medium text-secondary-800 mb-3">选择场景</h3>
      <RadioGroup value={selectedScenario} onChange={handleSelect}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {scenarios.map((scenario) => (
            <RadioGroup.Option
              key={scenario.id}
              value={scenario}
              className={({ active, checked }) => `
                ${checked ? 'bg-primary-50 border-primary-500' : 'bg-white border-gray-200'}
                ${active ? 'ring-2 ring-primary-500 ring-opacity-60' : ''}
                relative rounded-lg border-2 p-4 cursor-pointer transition-all duration-200
              `}
            >
              {({ checked }) => (
                <>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="text-sm">
                        <RadioGroup.Label
                          as="p"
                          className={`font-medium ${checked ? 'text-primary-600' : 'text-secondary-800'}`}
                        >
                          {scenario.name}
                        </RadioGroup.Label>
                        <RadioGroup.Description
                          as="span"
                          className={`inline ${checked ? 'text-primary-500' : 'text-secondary-500'}`}
                        >
                          {scenario.description}
                        </RadioGroup.Description>
                      </div>
                    </div>
                    {checked && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="flex-shrink-0 text-primary-500"
                      >
                        <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                        </svg>
                      </motion.div>
                    )}
                  </div>
                </>
              )}
            </RadioGroup.Option>
          ))}
        </div>
      </RadioGroup>
    </div>
  )
}

export default ScenarioSelector 