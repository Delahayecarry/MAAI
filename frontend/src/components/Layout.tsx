import { Outlet, NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'

const Layout = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <motion.div
                  initial={{ rotate: -10 }}
                  animate={{ rotate: 10 }}
                  transition={{ 
                    repeat: Infinity, 
                    repeatType: "reverse", 
                    duration: 1.5 
                  }}
                >
                  <span className="text-2xl">🤖</span>
                </motion.div>
                <h1 className="ml-2 text-xl font-bold text-primary-600">多智能体交互系统</h1>
              </div>
              <nav className="ml-10 flex items-center space-x-4">
                <NavLink 
                  to="/" 
                  className={({ isActive }) => 
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive 
                        ? 'bg-primary-50 text-primary-600' 
                        : 'text-secondary-500 hover:bg-gray-50'
                    }`
                  }
                  end
                >
                  主页
                </NavLink>
                <NavLink 
                  to="/live-chat" 
                  className={({ isActive }) => 
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive 
                        ? 'bg-primary-50 text-primary-600' 
                        : 'text-secondary-500 hover:bg-gray-50'
                    }`
                  }
                >
                  实时对话
                </NavLink>
                <NavLink 
                  to="/history" 
                  className={({ isActive }) => 
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive 
                        ? 'bg-primary-50 text-primary-600' 
                        : 'text-secondary-500 hover:bg-gray-50'
                    }`
                  }
                >
                  历史记录
                </NavLink>
              </nav>
            </div>
          </div>
        </div>
      </header>
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-secondary-500">
            © {new Date().getFullYear()} 多智能体交互系统 | 基于 React + FastAPI + SSE
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout 