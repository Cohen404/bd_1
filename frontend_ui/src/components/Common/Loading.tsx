import React from 'react';
import { Brain } from 'lucide-react';

interface LoadingProps {
  text?: string;
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
}

const Loading: React.FC<LoadingProps> = ({ 
  text = '加载中...', 
  size = 'medium', 
  fullScreen = false 
}) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  const containerClasses = fullScreen 
    ? 'fixed inset-0 bg-background flex items-center justify-center z-50'
    : 'flex items-center justify-center p-8';

  return (
    <div className={containerClasses}>
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          {/* 旋转的大脑图标 */}
          <Brain 
            className={`${sizeClasses[size]} text-primary-600 animate-spin`} 
          />
          {/* 脉冲效果 */}
          <div className={`absolute inset-0 ${sizeClasses[size]} bg-primary-600 rounded-full opacity-25 animate-ping`} />
        </div>
        
        <div className="text-center">
          <p className="text-gray-600 font-medium">{text}</p>
          <div className="flex space-x-1 mt-2 justify-center">
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Loading; 