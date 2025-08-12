import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Users, 
  Shield, 
  Database, 
  Brain, 
  FileText, 
  Settings, 
  FileBarChart,
  ChevronLeft,
  ChevronDown,
  ChevronRight,
  Activity
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { MenuItem } from '@/types';
import clsx from 'clsx';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const { user } = useAuth();
  const [expandedMenus, setExpandedMenus] = useState<string[]>(['admin-menu']);

  const toggleMenu = (key: string) => {
    setExpandedMenus(prev => 
      prev.includes(key) 
        ? prev.filter(k => k !== key)
        : [...prev, key]
    );
  };

  // 普通用户菜单
  const userMenuItems: MenuItem[] = [
    {
      key: 'dashboard',
      label: '控制台',
      icon: Home,
      path: '/dashboard'
    },
    {
      key: 'health-evaluate',
      label: '健康评估',
      icon: Activity,
      path: '/health-evaluate'
    },
    {
      key: 'data-manage',
      label: '数据管理',
      icon: Database,
      path: '/data-manage'
    },
    {
      key: 'result-manage',
      label: '结果管理',
      icon: FileBarChart,
      path: '/result-manage'
    },
  ];

  // 管理员专用菜单（二级菜单结构）
  const adminMenuItems: MenuItem[] = [
    {
      key: 'admin',
      label: '管理控制台',
      icon: Home,
      path: '/admin',
      children: [
        {
          key: 'user-manage',
          label: '用户管理',
          icon: Users,
          path: '/admin/user-manage',
          permission: 'PERM_USER_MANAGE'
        },
        {
          key: 'role-manage',
          label: '角色管理',
          icon: Shield,
          path: '/admin/role-manage',
          permission: 'PERM_ROLE_MANAGE'
        },
        {
          key: 'model-manage',
          label: '模型管理',
          icon: Brain,
          path: '/admin/model-manage',
          permission: 'PERM_MODEL_MANAGE'
        },
        {
          key: 'parameter-manage',
          label: '参数管理',
          icon: Settings,
          path: '/admin/parameter-manage',
          permission: 'PERM_PARAM_MANAGE'
        },
        {
          key: 'log-manage',
          label: '日志管理',
          icon: FileText,
          path: '/admin/log-manage',
          permission: 'PERM_LOG_MANAGE'
        },
      ]
    }
  ];

  // 根据用户类型显示不同菜单
  const displayMenuItems = user?.user_type === 'admin' ? 
    [...userMenuItems, ...adminMenuItems] : 
    userMenuItems;

  // 渲染菜单项
  const renderMenuItem = (item: MenuItem, isChild = false) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedMenus.includes(item.key);
    
    if (hasChildren) {
      return (
        <li key={item.key}>
          {/* 父级菜单项 */}
          <div className="space-y-1">
            <div
              className={clsx(
                'flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors cursor-pointer group',
                'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
              onClick={() => !collapsed && toggleMenu(item.key)}
            >
              <item.icon className={clsx(
                'flex-shrink-0 h-5 w-5',
                collapsed ? 'mx-auto' : 'mr-3'
              )} />
              {!collapsed && (
                <>
                  <span className="truncate flex-1">{item.label}</span>
                  {hasChildren && (
                    isExpanded ? 
                      <ChevronDown className="h-4 w-4" /> : 
                      <ChevronRight className="h-4 w-4" />
                  )}
                </>
              )}
            </div>

            {/* 子菜单 */}
            {!collapsed && isExpanded && (
              <ul className="ml-6 space-y-1">
                {item.children?.map(child => renderMenuItem(child, true))}
              </ul>
            )}
          </div>
        </li>
      );
    }

    // 叶子菜单项
    return (
      <li key={item.key}>
        <NavLink
          to={item.path}
          className={({ isActive }) =>
            clsx(
              'flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors group',
              isChild && 'pl-6',
              isActive
                ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
            )
          }
        >
          <item.icon className={clsx(
            'flex-shrink-0 h-5 w-5',
            collapsed ? 'mx-auto' : (isChild ? 'mr-3' : 'mr-3')
          )} />
          {!collapsed && (
            <span className="truncate">{item.label}</span>
          )}
        </NavLink>
      </li>
    );
  };

  return (
    <div className={clsx(
      'bg-white border-r border-gray-200 transition-all duration-300 flex flex-col shadow-lg',
      collapsed ? 'w-16' : 'w-64'
    )}>
      {/* Logo区域 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!collapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-gray-900">健康评估</span>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <ChevronLeft className={clsx(
            'h-4 w-4 transition-transform duration-300',
            collapsed && 'rotate-180'
          )} />
        </button>
      </div>

      {/* 用户信息 */}
      {!collapsed && user && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
              <Users className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user.username}
              </p>
              <p className="text-xs text-gray-500">
                {user.user_type === 'admin' ? '系统管理员' : '普通用户'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 导航菜单 */}
      <nav className="flex-1 py-4 overflow-y-auto custom-scrollbar">
        <ul className="space-y-1 px-3">
          {displayMenuItems.map(item => renderMenuItem(item))}
        </ul>
      </nav>

      {/* 底部状态 */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>系统运行正常</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar; 