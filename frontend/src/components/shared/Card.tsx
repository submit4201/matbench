import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// ═══════════════════════════════════════════════════════════════════════
// Card Component
// Glassmorphism card variants with framer-motion animations
// ═══════════════════════════════════════════════════════════════════════

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'glass' | 'solid' | 'outline' | 'glow';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  children: React.ReactNode;
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
};

const variantClasses = {
  glass: 'bg-white/5 backdrop-blur-md border border-white/10',
  solid: 'bg-slate-800/90 border border-slate-700',
  outline: 'bg-transparent border border-slate-600',
  glow: 'bg-white/5 backdrop-blur-md border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.15)]',
};

export function Card({
  variant = 'glass',
  padding = 'md',
  hover = true,
  className,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={twMerge(
        clsx(
          'rounded-xl transition-all duration-200',
          variantClasses[variant],
          paddingClasses[padding],
          hover && 'hover:border-white/20 hover:bg-white/[0.07]',
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// ─── Stat Card Variant ──────────────────────────────────────────────────
interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: { value: number; isPositive: boolean };
  className?: string;
}

export function StatCard({ label, value, icon, trend, className }: StatCardProps) {
  return (
    <Card variant="glass" className={twMerge('flex items-start gap-3', className)}>
      {icon && (
        <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <p className="text-xs text-slate-400 uppercase tracking-wide">{label}</p>
        <p className="text-xl font-semibold text-white truncate">{value}</p>
        {trend && (
          <p
            className={clsx(
              'text-xs mt-1',
              trend.isPositive ? 'text-emerald-400' : 'text-red-400'
            )}
          >
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </p>
        )}
      </div>
    </Card>
  );
}

// ─── Action Card Variant ────────────────────────────────────────────────
interface ActionCardProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export function ActionCard({
  title,
  description,
  icon,
  onClick,
  disabled = false,
  className,
}: ActionCardProps) {
  return (
    <Card
      variant="outline"
      hover={!disabled}
      className={twMerge(
        clsx(
          'cursor-pointer group',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )
      )}
      onClick={disabled ? undefined : onClick}
    >
      <div className="flex items-center gap-3">
        {icon && (
          <div className="p-2 rounded-lg bg-slate-700 text-slate-300 group-hover:bg-emerald-500/20 group-hover:text-emerald-400 transition-colors">
            {icon}
          </div>
        )}
        <div className="flex-1">
          <p className="font-medium text-white group-hover:text-emerald-300 transition-colors">
            {title}
          </p>
          {description && <p className="text-xs text-slate-400">{description}</p>}
        </div>
      </div>
    </Card>
  );
}

export default Card;
