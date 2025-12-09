/**
 * CalendarWidget.tsx - Week Schedule & Upcoming Events
 * 
 * A sleek calendar widget featuring:
 * - Week grid with day indicators
 * - Upcoming scheduled actions
 * - Category color coding
 * - Quick stats summary
 */

import { useState, useEffect } from 'react';
import type { CalendarStats, ScheduledAction } from '../types';

// Category styling
const CATEGORY_STYLES: Record<string, { color: string; icon: string }> = {
  payment: { color: 'bg-rose-500', icon: '💰' },
  supply_order: { color: 'bg-blue-500', icon: '📦' },
  maintenance: { color: 'bg-amber-500', icon: '🔧' },
  marketing: { color: 'bg-purple-500', icon: '📢' },
  meeting: { color: 'bg-cyan-500', icon: '🤝' },
  custom: { color: 'bg-slate-500', icon: '📌' },
};

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

interface CalendarWidgetProps {
  agentId?: string;
  currentWeek?: number;
}

export function CalendarWidget({ agentId = 'p1', currentWeek = 1 }: CalendarWidgetProps) {
  const [stats, setStats] = useState<CalendarStats | null>(null);
  const [schedule, setSchedule] = useState<Record<number, ScheduledAction[]>>({});
  const [loading, setLoading] = useState(true);

  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Modal State
  const [actionType, setActionType] = useState('marketing');
  const [actionTitle, setActionTitle] = useState('');
  const [actionPriority, setActionPriority] = useState('medium');

  useEffect(() => {
    fetchCalendar();
  }, [agentId, currentWeek]);

  const fetchCalendar = async () => {
    try {
      const res = await fetch(`http://localhost:8000/calendar/${agentId}?week=${currentWeek}`);
      const data = await res.json();
      setStats(data.statistics);
      setSchedule(data.schedule || {});
    } catch (err) {
      console.error('Failed to fetch calendar:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDayClick = (day: number) => {
    setSelectedDay(day);
    setModalOpen(true);
    setActionTitle('');
  };

  const handleScheduleAction = async () => {
    if (!selectedDay) return;

    try {
      const res = await fetch(`http://localhost:8000/calendar/${agentId}/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          day: selectedDay,
          category: actionType,
          title: actionTitle || `${actionType.charAt(0).toUpperCase() + actionType.slice(1)} Action`,
          priority: actionPriority
        })
      });

      if (res.ok) {
        setModalOpen(false);
        fetchCalendar(); // Refresh
      } else {
        console.error('Failed to schedule action');
      }
    } catch (err) {
      console.error('Error scheduling action:', err);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-5 animate-pulse h-64 border border-slate-700" />
    );
  }

  // Group actions by day
  const dayActions = DAYS.map((_, idx) => schedule[idx + 1] || []);

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl overflow-hidden shadow-lg border border-slate-700 h-full flex flex-col">
      {/* Header */}
      <div className="bg-slate-900/50 px-5 py-4 border-b border-slate-700 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                <span className="text-xl">📅</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Week {currentWeek}</h3>
              <p className="text-xs text-slate-400">Tap a day to schedule</p>
            </div>
          </div>
          {stats && (
            <div className="flex gap-2">
              <StatBadge value={stats.upcoming} label="Pending" color="bg-indigo-500" />
              <StatBadge value={stats.overdue} label="Overdue" color="bg-rose-500" />
            </div>
          )}
        </div>
      </div>

      {/* Week Grid */}
      <div className="p-5 flex-1 flex flex-col min-h-0">
        <div className="grid grid-cols-7 gap-2 mb-4 flex-shrink-0">
          {DAYS.map((day, idx) => {
            const dayNum = idx + 1;
            const actions = dayActions[idx];
            const hasActions = actions.length > 0;
            
            return (
              <div 
                key={day}
                onClick={() => handleDayClick(dayNum)}
                className={`relative text-center py-3 rounded-xl transition-all duration-200 border cursor-pointer hover:scale-105 active:scale-95 group
                  ${hasActions 
                    ? 'bg-indigo-600/20 border-indigo-500/30 hover:bg-indigo-600/30 shadow-[0_0_10px_rgba(79,70,229,0.1)]' 
                    : 'bg-slate-800/50 border-slate-700 hover:border-slate-500 hover:bg-slate-750'
                  }`}
              >
                <div className={`text-[10px] font-bold uppercase tracking-wider mb-0.5 ${hasActions ? 'text-indigo-300' : 'text-slate-500 group-hover:text-slate-300'}`}>
                  {day}
                </div>
                <div className={`text-lg font-bold ${hasActions ? 'text-white' : 'text-slate-400 group-hover:text-white'}`}>
                  {dayNum}
                </div>
                
                {/* Action Indicator Dots */}
                {hasActions && (
                  <div className="absolute -bottom-1.5 left-1/2 transform -translate-x-1/2 flex gap-0.5 bg-slate-900/80 px-1.5 py-0.5 rounded-full border border-slate-700">
                    {actions.slice(0, 3).map((action, i) => (
                      <div 
                        key={i}
                        className={`w-1.5 h-1.5 rounded-full ${
                          CATEGORY_STYLES[action.category]?.color.replace('bg-', 'bg-') || 'bg-indigo-500'
                        }`}
                      />
                    ))}
                    {actions.length > 3 && (
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Upcoming Actions List */}
        <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3 flex-shrink-0 flex items-center justify-between">
            <span>Upcoming This Week</span>
            <span className="bg-slate-800 px-2 py-0.5 rounded text-[10px] border border-slate-700">
                {Object.values(schedule).flat().length} Events
            </span>
          </h4>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1">
            {Object.values(schedule).flat().length === 0 ? (
              <div className="bg-slate-800/50 border border-slate-700/50 border-dashed rounded-xl p-8 text-center flex flex-col items-center justify-center h-full group cursor-pointer hover:bg-slate-800 transition-colors"
                onClick={() => handleDayClick(1)} // Default to day 1 on empty click
              >
                 <div className="w-12 h-12 rounded-full bg-slate-700/50 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                   <span className="text-2xl text-slate-400">+</span>
                 </div>
                 <p className="text-slate-400 font-medium text-sm">No scheduled events</p>
                 <p className="text-slate-500 text-xs mt-1">Tap here or any day to plan</p>
              </div>
            ) : (
                Object.entries(schedule).flatMap(([day, actions]) =>
                  (actions as ScheduledAction[]).map((action) => (
                    <ActionItem key={action.id} action={action} day={parseInt(day)} />
                  ))
                ).slice(0, 20) // Show more items since we have space
            )}
          </div>
        </div>
      </div>

      {/* Schedule Modal */}
      {modalOpen && (
        <div className="absolute inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5 w-full max-w-xs shadow-2xl relative animate-scale-in">
            <button 
                onClick={() => setModalOpen(false)}
                className="absolute top-3 right-3 text-slate-400 hover:text-white transition-colors"
            >
                ✕
            </button>
            
            <h3 className="text-lg font-bold text-white mb-1">Schedule Event</h3>
            <p className="text-sm text-slate-400 mb-4">Planning for Day {selectedDay}</p>
            
            <div className="space-y-3">
                <div>
                    <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">Type</label>
                    <div className="grid grid-cols-3 gap-2">
                        {['marketing', 'maintenance', 'supply_order', 'meeting', 'payment', 'custom'].map(type => (
                            <button
                                key={type}
                                onClick={() => setActionType(type)}
                                className={`text-xs py-2 px-1 rounded-lg border transition-all flex flex-col items-center gap-1 ${
                                    actionType === type 
                                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg' 
                                    : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                                }`}
                            >
                                <span>{CATEGORY_STYLES[type]?.icon}</span>
                                <span className="capitalize text-[9px]">{type.split('_')[0]}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">Title</label>
                    <input 
                        type="text" 
                        value={actionTitle}
                        onChange={(e) => setActionTitle(e.target.value)}
                        placeholder="e.g. Deep Clean Machines"
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                </div>

                 <div>
                    <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">Priority</label>
                    <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-700">
                        {['low', 'medium', 'high', 'critical'].map(p => (
                            <button
                                key={p}
                                onClick={() => setActionPriority(p)}
                                className={`flex-1 py-1 text-[10px] font-bold uppercase rounded-md transition-all ${
                                    actionPriority === p
                                    ? p === 'critical' ? 'bg-rose-500 text-white' : 
                                      p === 'high' ? 'bg-orange-500 text-white' :
                                      p === 'medium' ? 'bg-yellow-500 text-black' : 'bg-emerald-500 text-white'
                                    : 'text-slate-500 hover:text-slate-300'
                                }`}
                            >
                                {p}
                            </button>
                        ))}
                    </div>
                </div>
                
                <button 
                    onClick={handleScheduleAction}
                    className="w-full py-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl font-bold text-white shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-[1.02] active:scale-95 transition-all mt-2"
                >
                    Confirm Schedule
                </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Stat Badge
function StatBadge({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div className="text-center group cursor-help relative">
      <div className={`${color} text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-lg`}>
        {value}
      </div>
       {/* Tooltip could go here */}
    </div>
  );
}

// Action List Item
function ActionItem({ action, day }: { action: ScheduledAction; day: number }) {
  const style = CATEGORY_STYLES[action.category] || CATEGORY_STYLES.custom;
  const priorityColors = {
    critical: 'text-rose-400',
    high: 'text-orange-400',
    medium: 'text-amber-400',
    low: 'text-emerald-400',
  };

  return (
    <div className="flex items-center gap-3 bg-slate-800/40 border border-slate-700/50 rounded-xl p-2.5 hover:bg-slate-700/50 hover:border-slate-600 transition-all cursor-pointer group hover:translate-x-1">
      <div className={`w-8 h-8 rounded-lg ${style.color} bg-opacity-20 flex items-center justify-center flex-shrink-0 text-white border border-white/10 shadow-sm`}>
        <span className="text-sm shadow-black drop-shadow-md">{style.icon}</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-200 text-sm truncate group-hover:text-white transition-colors">{action.title}</span>
          {action.is_recurring && (
            <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-1 py-0.5 rounded border border-indigo-500/20">Repeat</span>
          )}
        </div>
        <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-0.5">
          <span className="bg-slate-700/50 px-1.5 rounded text-slate-400">Day {day}</span>
          {/* <span>•</span> */}
          <span className={`font-bold uppercase tracking-wider ${priorityColors[action.priority] || 'text-slate-400'}`}>
            {action.priority}
          </span>
        </div>
      </div>
      <div className="opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0">
        <span className="text-slate-400 hover:text-white text-xs">Edit</span>
      </div>
    </div>
  );
}

export default CalendarWidget;
