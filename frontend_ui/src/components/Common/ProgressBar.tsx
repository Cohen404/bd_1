import React from 'react';
import { CheckCircle, XCircle, Clock, Play } from 'lucide-react';

interface ProgressBarProps {
  progress: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  title?: string;
  showIcon?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const ProgressBar: React.FC<ProgressBarProps> = ({ 
  progress, 
  status, 
  title, 
  showIcon = true,
  size = 'medium'
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'processing':
        return 'bg-blue-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-300';
    }
  };

  const getBackgroundColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-100';
      case 'processing':
        return 'bg-blue-100';
      case 'failed':
        return 'bg-red-100';
      default:
        return 'bg-gray-100';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Play className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'processing':
        return '处理中';
      case 'failed':
        return '失败';
      default:
        return '等待中';
    }
  };

  const sizeClasses = {
    small: 'h-2',
    medium: 'h-3',
    large: 'h-4'
  };

  return (
    <div className="w-full">
      {title && (
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">{title}</span>
          <div className="flex items-center space-x-1">
            {showIcon && getStatusIcon()}
            <span className="text-xs text-gray-500">{getStatusText()}</span>
          </div>
        </div>
      )}
      
      <div className={`w-full ${getBackgroundColor()} rounded-full ${sizeClasses[size]}`}>
        <div
          className={`${getStatusColor()} ${sizeClasses[size]} rounded-full transition-all duration-300 ease-in-out`}
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
      
      <div className="flex justify-between items-center mt-1">
        <span className="text-xs text-gray-500">{progress}%</span>
        {status === 'processing' && (
          <span className="text-xs text-blue-500 animate-pulse">正在处理...</span>
        )}
      </div>
    </div>
  );
};

export default ProgressBar; 