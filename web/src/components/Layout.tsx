import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const tabs = [
    { path: '/home', label: '首页' },
    { path: '/add', label: '添加' },
    { path: '/display', label: '展示' },
  ]

  return (
    <div className="layout">
      <header className="header">
        <h1 className="header-title">ZAccount</h1>
        <nav className="nav">
          {tabs.map((tab) => (
            <Link
              key={tab.path}
              to={tab.path}
              className={`nav-link ${location.pathname === tab.path ? 'active' : ''}`}
            >
              {tab.label}
            </Link>
          ))}
        </nav>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout

