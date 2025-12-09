import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// ═══════════════════════════════════════════════════════════════════════
// Badge Component
// Status badges with semantic colors
// ═══════════════════════════════════════════════════════════════════════

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'premium';
  size?: 'sm' | 'md';
  dot?: boolean;
  children: React.ReactNode;
  className?: string;
}

const variantClasses = {
  default: 'bg-slate-700 text-slate-300 border-slate-600',
  success: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  danger: 'bg-red-500/20 text-red-400 border-red-500/30',
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  premium: 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-300 border-purple-500/30',
};

const dotColors = {
  default: 'bg-slate-400',
  success: 'bg-emerald-400',
  warning: 'bg-amber-400',
  danger: 'bg-red-400',
  info: 'bg-blue-400',
  premium: 'bg-purple-400',
};

const sizeClasses = {
  sm: 'px-1.5 py-0.5 text-[10px]',
  md: 'px-2 py-1 text-xs',
};

export function Badge({
  variant = 'default',
  size = 'md',
  dot = false,
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 font-medium rounded-full border',
          variantClasses[variant],
          sizeClasses[size],
          className
        )
      )}
    >
      {dot && (
        <span
          className={clsx('w-1.5 h-1.5 rounded-full animate-pulse', dotColors[variant])}
        />
      )}
      {children}
    </span>
  );
}

// ─── Notification Dot ───────────────────────────────────────────────────
interface NotificationDotProps {
  count?: number;
  className?: string;
}

export function NotificationDot({ count, className }: NotificationDotProps) {
  if (!count || count === 0) return null;
  
  return (
    <span
      className={twMerge(
        'absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center',
        'bg-red-500 text-white text-[10px] font-bold rounded-full',
        'animate-bounce-in',
        className
      )}
    >
      {count > 99 ? '99+' : count}
    </span>
  );
}

export default Badge;
