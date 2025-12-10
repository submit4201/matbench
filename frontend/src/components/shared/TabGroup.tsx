import React from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// ═══════════════════════════════════════════════════════════════════════
// TabGroup Component
// Radix Tabs with custom styling
// ═══════════════════════════════════════════════════════════════════════

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: number;
}

interface TabGroupProps {
  tabs: Tab[];
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export function TabGroup({
  tabs,
  defaultValue,
  value,
  onValueChange,
  children,
  className,
}: TabGroupProps) {
  return (
    <Tabs.Root
      defaultValue={defaultValue || tabs[0]?.id}
      value={value}
      onValueChange={onValueChange}
      className={twMerge('flex flex-col', className)}
    >
      <Tabs.List className="flex gap-1 p-1 bg-slate-800/50 rounded-lg border border-slate-700 mb-4">
        {tabs.map((tab) => (
          <Tabs.Trigger
            key={tab.id}
            value={tab.id}
            className={clsx(
              'flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all',
              'text-slate-400 hover:text-white hover:bg-white/5',
              'data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400',
              'focus:outline-none focus:ring-2 focus:ring-emerald-500/50'
            )}
          >
            {tab.icon}
            {tab.label}
            {tab.badge !== undefined && tab.badge > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-[10px] font-bold bg-red-500 text-white rounded-full">
                {tab.badge > 99 ? '99+' : tab.badge}
              </span>
            )}
          </Tabs.Trigger>
        ))}
      </Tabs.List>
      {children}
    </Tabs.Root>
  );
}

// ─── Tab Content ────────────────────────────────────────────────────────
interface TabContentProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export function TabContent({ value, children, className }: TabContentProps) {
  return (
    <Tabs.Content
      value={value}
      className={twMerge(
        'flex-1 focus:outline-none animate-fade-in',
        className
      )}
    >
      {children}
    </Tabs.Content>
  );
}

export default TabGroup;
