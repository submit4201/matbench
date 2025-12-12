import { useState, useEffect } from 'react';
import {
    Calendar,
    Clock,
    ChevronLeft,
    ChevronRight,
    Plus,
    Package,
    Wrench,
    Megaphone,
    DollarSign,
    MessageSquare,
    RefreshCw,
    Trash2,
    Edit3,
    X,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Button, Modal } from '../shared';
import { toast } from 'sonner';

// ═══════════════════════════════════════════════════════════════════════
// CalendarPanel Component - Week/Month views with action CRUD
// ═══════════════════════════════════════════════════════════════════════

interface ScheduledAction {
    id: string;
    title: string;
    description: string;
    category: string;
    priority: string;
    week: number;
    day: number;
    is_recurring: boolean;
    recurrence_weeks: number;
    completed: boolean;
}

interface CalendarData {
    week: number;
    schedule: Record<string, ScheduledAction[]>;
    statistics: {
        total_scheduled: number;
        completed: number;
        recurring: number;
        by_category: Record<string, number>;
    };
}

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
    payment: <DollarSign className="w-4 h-4" />,
    supply_order: <Package className="w-4 h-4" />,
    maintenance: <Wrench className="w-4 h-4" />,
    marketing: <Megaphone className="w-4 h-4" />,
    negotiation: <MessageSquare className="w-4 h-4" />,
    custom: <Clock className="w-4 h-4" />,
};

const PRIORITY_COLORS: Record<string, string> = {
    low: 'bg-slate-500/20 border-slate-500/50 text-slate-300',
    medium: 'bg-blue-500/20 border-blue-500/50 text-blue-300',
    high: 'bg-amber-500/20 border-amber-500/50 text-amber-300',
    critical: 'bg-red-500/20 border-red-500/50 text-red-300',
};

export default function CalendarPanel() {
    const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
    const [monthData, setMonthData] = useState<Record<number, CalendarData>>({});
    const [viewWeek, setViewWeek] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [selectedDay, setSelectedDay] = useState<number>(1);
    const [selectedWeek, setSelectedWeek] = useState<number>(1);
    const [viewMode, setViewMode] = useState<'week' | 'month'>('week');
    const [selectedAction, setSelectedAction] = useState<ScheduledAction | null>(null);
    const [showDetailModal, setShowDetailModal] = useState(false);
    const { gameState } = useGameStore();

    const fetchCalendar = async (week?: number) => {
        setLoading(true);
        try {
            const url = week
                ? `http://localhost:8000/calendar/p1?week=${week}`
                : 'http://localhost:8000/calendar/p1';
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                setCalendarData(data);
                if (viewWeek === null) setViewWeek(data.week);
            }
        } catch (err) {
            console.error('Failed to fetch calendar:', err);
        }
        setLoading(false);
    };

    const fetchMonth = async (startWeek: number) => {
        setLoading(true);
        const weekPromises = [];
        for (let i = 0; i < 4; i++) {
            const w = startWeek + i;
            weekPromises.push(
                fetch(`http://localhost:8000/calendar/p1?week=${w}`)
                    .then(r => r.ok ? r.json() : null)
                    .catch(() => null)
            );
        }
        const results = await Promise.all(weekPromises);
        const newMonthData: Record<number, CalendarData> = {};
        results.forEach((data, idx) => {
            if (data) newMonthData[startWeek + idx] = data;
        });
        setMonthData(newMonthData);
        setLoading(false);
    };

    const refreshData = () => {
        if (viewMode === 'week') fetchCalendar(viewWeek ?? undefined);
        else fetchMonth(viewWeek ?? 1);
    };

    useEffect(() => {
        fetchCalendar();
    }, [gameState?.week]);

    useEffect(() => {
        if (viewWeek !== null) refreshData();
    }, [viewWeek, viewMode]);

    const handlePrevWeek = () => {
        if (viewWeek && viewWeek > 1) {
            setViewWeek(viewMode === 'month' ? Math.max(1, viewWeek - 4) : viewWeek - 1);
        }
    };

    const handleNextWeek = () => {
        if (viewWeek) {
            setViewWeek(viewMode === 'month' ? viewWeek + 4 : viewWeek + 1);
        }
    };

    const getActionsForDay = (day: number, weekNum?: number): ScheduledAction[] => {
        if (viewMode === 'month' && weekNum !== undefined) {
            const weekData = monthData[weekNum];
            if (!weekData?.schedule) return [];
            return weekData.schedule[day.toString()] || [];
        }
        if (!calendarData?.schedule) return [];
        return calendarData.schedule[day.toString()] || [];
    };

    const openAddModal = (day: number, week: number) => {
        setSelectedDay(day);
        setSelectedWeek(week);
        setShowAddModal(true);
    };

    const openDetailModal = (action: ScheduledAction, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedAction(action);
        setShowDetailModal(true);
    };

    const handleDeleteAction = async (actionId: string) => {
        try {
            const res = await fetch(`http://localhost:8000/calendar/p1/action/${actionId}`, {
                method: 'DELETE',
            });
            if (res.ok) {
                toast.success('Action deleted');
                setShowDetailModal(false);
                refreshData();
            } else {
                toast.error('Failed to delete');
            }
        } catch {
            toast.error('Error deleting action');
        }
    };

    return (
        <div className="space-y-4 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-2">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-purple-400" />
                    Calendar
                </h2>
                <div className="flex items-center gap-1.5">
                    {/* View Toggle */}
                    <div className="flex rounded-md overflow-hidden border border-white/20 text-xs">
                        <button
                            className={`px-2 py-1 ${viewMode === 'week' ? 'bg-purple-500 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                            onClick={() => setViewMode('week')}
                        >
                            Week
                        </button>
                        <button
                            className={`px-2 py-1 ${viewMode === 'month' ? 'bg-purple-500 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                            onClick={() => setViewMode('month')}
                        >
                            Month
                        </button>
                    </div>
                    <Button variant="secondary" size="sm" onClick={refreshData}>
                        <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button variant="primary" size="sm" onClick={() => openAddModal(1, viewWeek ?? 1)}>
                        <Plus className="w-3.5 h-3.5" />
                    </Button>
                </div>
            </div>

            {/* Week View */}
            {viewMode === 'week' && (
                <Card variant="glass" className="p-3">
                    <div className="flex items-center justify-between mb-3">
                        <button
                            onClick={handlePrevWeek}
                            className="p-1.5 rounded hover:bg-white/10 transition-colors disabled:opacity-50"
                            disabled={!viewWeek || viewWeek <= 1}
                        >
                            <ChevronLeft className="w-4 h-4 text-slate-300" />
                        </button>
                        <div className="text-center">
                            <h3 className="text-base font-semibold text-white">Week {viewWeek ?? '...'}</h3>
                            {calendarData && (
                                <p className="text-[10px] text-slate-400">
                                    {calendarData.statistics.total_scheduled} scheduled
                                </p>
                            )}
                        </div>
                        <button onClick={handleNextWeek} className="p-1.5 rounded hover:bg-white/10 transition-colors">
                            <ChevronRight className="w-4 h-4 text-slate-300" />
                        </button>
                    </div>
                    <div className="grid grid-cols-7 gap-1.5">
                        {DAY_NAMES.map((dayName, index) => {
                            const dayNum = index + 1;
                            const actions = getActionsForDay(dayNum);
                            const hasActions = actions.length > 0;

                            // Determine if this is "Today"
                            const currentDayIndex = DAY_NAMES.indexOf(gameState?.day ?? '') + 1;
                            const currentWeek = gameState?.week ?? 1;
                            const isToday = viewWeek === currentWeek && dayNum === currentDayIndex;

                            return (
                                <div
                                    key={dayName}
                                    className={`
                                        relative p-2 rounded-lg border transition-all cursor-pointer min-h-[150px] flex flex-col
                                        ${isToday
                                            ? 'bg-emerald-500/10 border-emerald-400 ring-1 ring-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.15)]'
                                            : hasActions
                                                ? 'bg-purple-500/5 border-purple-500/20 hover:bg-purple-500/10'
                                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                                        }
                                    `}
                                    onClick={() => openAddModal(dayNum, viewWeek ?? 1)}
                                >
                                    {/* Header: Day Name + Today Badge */}
                                    <div className="flex items-center justify-between mb-2">
                                        <p className={`text-xs font-semibold ${isToday ? 'text-emerald-400' : 'text-slate-400'}`}>
                                            {dayName}
                                        </p>
                                        {isToday && (
                                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500 text-white shadow-sm">
                                                TODAY
                                            </span>
                                        )}
                                    </div>

                                    {/* Content Area */}
                                    <div className="flex-1 space-y-1">
                                        {hasActions ? (
                                            <>
                                                {actions.slice(0, 5).map((action) => (
                                                    <div
                                                        key={action.id}
                                                        className={`
                                                            group flex items-center gap-1.5 p-1.5 rounded border text-[11px] 
                                                            transition-transform hover:scale-[1.02] active:scale-95
                                                            ${PRIORITY_COLORS[action.priority] || PRIORITY_COLORS.low}
                                                        `}
                                                        title={action.title}
                                                        onClick={(e) => openDetailModal(action, e)}
                                                    >
                                                        {CATEGORY_ICONS[action.category] || CATEGORY_ICONS.custom}
                                                        <span className="truncate font-medium">{action.title}</span>
                                                    </div>
                                                ))}
                                                {actions.length > 5 && (
                                                    <p className="text-[10px] text-slate-500 text-center font-medium py-1">
                                                        +{actions.length - 5} more
                                                    </p>
                                                )}
                                            </>
                                        ) : (
                                            /* Empty State Placeholder */
                                            <div className="h-full flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                                                <Plus className="w-4 h-4 text-slate-500" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </Card>
            )
            }

            {/* Month View */}
            {
                viewMode === 'month' && (
                    <Card variant="glass" className="p-3">
                        <div className="flex items-center justify-between mb-3">
                            <button
                                onClick={handlePrevWeek}
                                className="p-1.5 rounded hover:bg-white/10 transition-colors disabled:opacity-50"
                                disabled={!viewWeek || viewWeek <= 1}
                            >
                                <ChevronLeft className="w-4 h-4 text-slate-300" />
                            </button>
                            <div className="text-center">
                                <h3 className="text-base font-semibold text-white">Weeks {viewWeek} - {(viewWeek ?? 1) + 3}</h3>
                            </div>
                            <button onClick={handleNextWeek} className="p-1.5 rounded hover:bg-white/10 transition-colors">
                                <ChevronRight className="w-4 h-4 text-slate-300" />
                            </button>
                        </div>

                        {/* Header */}
                        <div className="grid grid-cols-8 gap-0.5 mb-1">
                            <div className="text-[10px] text-slate-500 text-center p-0.5">Wk</div>
                            {DAY_NAMES.map((d) => (
                                <div key={d} className="text-[10px] text-slate-400 text-center p-0.5 font-medium">{d.slice(0, 2)}</div>
                            ))}
                        </div>

                        {/* Rows */}
                        <div className="space-y-0.5">
                            {[0, 1, 2, 3].map((offset) => {
                                const weekNum = (viewWeek ?? 1) + offset;
                                return (
                                    <div key={weekNum} className="grid grid-cols-8 gap-0.5">
                                        <div className="text-[10px] text-purple-400 font-bold p-1 flex items-center justify-center bg-purple-500/10 rounded">
                                            {weekNum}
                                        </div>
                                        {DAY_NAMES.map((_, dayIdx) => {
                                            const dayNum = dayIdx + 1;
                                            const actions = getActionsForDay(dayNum, weekNum);
                                            const hasActions = actions.length > 0;

                                            // Determine if this is "Today"
                                            const currentDayIndex = DAY_NAMES.indexOf(gameState?.day ?? '') + 1;
                                            const currentWeek = gameState?.week ?? 1;
                                            const isToday = weekNum === currentWeek && dayNum === currentDayIndex;

                                            return (
                                                <div
                                                    key={`${weekNum}-${dayNum}`}
                                                    className={`
                                                        p-1 rounded-md border cursor-pointer min-h-[80px] flex flex-col items-start justify-start relative transition-all
                                                        ${isToday
                                                            ? 'bg-emerald-500/10 border-emerald-400 ring-1 ring-emerald-400'
                                                            : hasActions
                                                                ? 'bg-purple-500/5 border-purple-500/20 hover:bg-purple-500/10'
                                                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                                                        }
                                                    `}
                                                    onClick={() => openAddModal(dayNum, weekNum)}
                                                >
                                                    {/* Day Number (if needed) or just status */}
                                                    {isToday && (
                                                        <div className="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_5px_rgba(16,185,129,0.8)]" />
                                                    )}

                                                    {/* Actions List */}
                                                    <div className="w-full space-y-0.5 mt-0.5">
                                                        {actions.slice(0, 3).map((action) => (
                                                            <div
                                                                key={action.id}
                                                                className={`
                                                                    text-[8px] px-1 py-0.5 rounded truncate w-full cursor-pointer hover:brightness-110
                                                                    ${PRIORITY_COLORS[action.priority] || 'bg-slate-700 text-slate-300'}
                                                                `}
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    openDetailModal(action, e);
                                                                }}
                                                                title={action.title}
                                                            >
                                                                {action.title}
                                                            </div>
                                                        ))}
                                                        {actions.length > 3 && (
                                                            <div className="text-[8px] text-slate-500 pl-0.5">
                                                                +{actions.length - 3} more
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                );
                            })}
                        </div>
                    </Card>
                )
            }

            {/* Stats (compact) */}
            {
                calendarData?.statistics && viewMode === 'week' && Object.keys(calendarData.statistics.by_category || {}).length > 0 && (
                    <div className="flex flex-wrap gap-2 text-[10px]">
                        {Object.entries(calendarData.statistics.by_category).map(([cat, count]) => (
                            <div key={cat} className="flex items-center gap-1 px-2 py-1 rounded bg-white/5 text-slate-300">
                                {CATEGORY_ICONS[cat] || CATEGORY_ICONS.custom}
                                <span className="capitalize">{cat.replace('_', ' ')}</span>
                                <span className="text-white font-medium">{count}</span>
                            </div>
                        ))}
                    </div>
                )
            }

            {/* Add Modal */}
            <AddActionModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                defaultDay={selectedDay}
                currentWeek={selectedWeek}
                onScheduled={() => {
                    setShowAddModal(false);
                    refreshData();
                }}
            />

            {/* Detail Modal */}
            <ActionDetailModal
                isOpen={showDetailModal}
                onClose={() => setShowDetailModal(false)}
                action={selectedAction}
                onDelete={handleDeleteAction}
                onUpdated={() => {
                    setShowDetailModal(false);
                    refreshData();
                }}
            />
        </div >
    );
}

// ─── Action Detail Modal ─────────────────────────────────────────────────────
interface ActionDetailModalProps {
    isOpen: boolean;
    onClose: () => void;
    action: ScheduledAction | null;
    onDelete: (id: string) => void;
    onUpdated: () => void;
}

function ActionDetailModal({ isOpen, onClose, action, onDelete, onUpdated }: ActionDetailModalProps) {
    const [editing, setEditing] = useState(false);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [week, setWeek] = useState(1);
    const [day, setDay] = useState(1);
    const [priority, setPriority] = useState('medium');
    const [isRecurring, setIsRecurring] = useState(false);
    const [recurrenceWeeks, setRecurrenceWeeks] = useState(1);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (action) {
            setTitle(action.title);
            setDescription(action.description || '');
            setWeek(action.week);
            setDay(action.day);
            setPriority(action.priority);
            setIsRecurring(action.is_recurring);
            setRecurrenceWeeks(action.recurrence_weeks || 1);
            setEditing(false);
        }
    }, [action]);

    const handleSave = async () => {
        if (!action) return;
        setSaving(true);
        try {
            const res = await fetch(`http://localhost:8000/calendar/p1/action/${action.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, week, day, priority, is_recurring: isRecurring, recurrence_weeks: recurrenceWeeks }),
            });
            if (res.ok) {
                toast.success('Updated');
                onUpdated();
            } else {
                toast.error('Failed to update');
            }
        } catch {
            toast.error('Error updating');
        }
        setSaving(false);
    };

    if (!action) return null;

    return (
        <Modal open={isOpen} onOpenChange={(open) => !open && onClose()} title={editing ? 'Edit Action' : 'Action Details'}>
            <div className="space-y-3">
                {!editing ? (
                    <>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                {CATEGORY_ICONS[action.category] || CATEGORY_ICONS.custom}
                                <h3 className="text-lg font-semibold text-white">{action.title}</h3>
                            </div>
                            {action.description && <p className="text-sm text-slate-400">{action.description}</p>}
                            <div className="flex flex-wrap gap-2 text-xs">
                                <span className={`px-2 py-0.5 rounded border ${PRIORITY_COLORS[action.priority]}`}>{action.priority}</span>
                                <span className="px-2 py-0.5 rounded bg-white/10 text-slate-300">Week {action.week}, {DAY_NAMES[action.day - 1]}</span>
                                {action.is_recurring && <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">Every {action.recurrence_weeks}w</span>}
                            </div>
                        </div>
                        <div className="flex gap-2 pt-2">
                            <Button variant="secondary" className="flex-1" onClick={() => setEditing(true)}>
                                <Edit3 className="w-3.5 h-3.5 mr-1" /> Edit
                            </Button>
                            <Button variant="primary" className="flex-1 !bg-red-600 hover:!bg-red-700" onClick={() => onDelete(action.id)}>
                                <Trash2 className="w-3.5 h-3.5 mr-1" /> Delete
                            </Button>
                        </div>
                    </>
                ) : (
                    <>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Title</label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="w-full px-2 py-1.5 text-sm rounded bg-white/10 border border-white/20 text-white"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Description</label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="w-full px-2 py-1.5 text-sm rounded bg-white/10 border border-white/20 text-white resize-none"
                                rows={2}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Week</label>
                                <input type="number" value={week} onChange={(e) => setWeek(parseInt(e.target.value) || 1)} min={1}
                                    className="w-full px-2 py-1.5 text-sm rounded bg-white/10 border border-white/20 text-white" />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Day</label>
                                <select value={day} onChange={(e) => setDay(parseInt(e.target.value))}
                                    className="w-full px-2 py-1.5 text-sm rounded bg-slate-700 border border-white/20 text-white">
                                    {DAY_NAMES.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}
                                </select>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Priority</label>
                            <select value={priority} onChange={(e) => setPriority(e.target.value)}
                                className="w-full px-2 py-1.5 text-sm rounded bg-slate-700 border border-white/20 text-white">
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="critical">Critical</option>
                            </select>
                        </div>
                        <div className="flex items-center gap-2">
                            <input type="checkbox" id="edit-recurring" checked={isRecurring} onChange={(e) => setIsRecurring(e.target.checked)} />
                            <label htmlFor="edit-recurring" className="text-xs text-slate-300">Recurring</label>
                            {isRecurring && (
                                <div className="flex items-center gap-1 ml-2">
                                    <span className="text-xs text-slate-400">every</span>
                                    <input type="number" value={recurrenceWeeks} onChange={(e) => setRecurrenceWeeks(Math.max(1, parseInt(e.target.value) || 1))}
                                        min={1} max={52} className="w-12 px-1 py-0.5 text-xs rounded bg-white/10 border border-white/20 text-white" />
                                    <span className="text-xs text-slate-400">weeks</span>
                                </div>
                            )}
                        </div>
                        <div className="flex gap-2 pt-2">
                            <Button variant="secondary" className="flex-1" onClick={() => setEditing(false)}>
                                <X className="w-3.5 h-3.5 mr-1" /> Cancel
                            </Button>
                            <Button variant="primary" className="flex-1" onClick={handleSave} disabled={saving}>
                                {saving ? 'Saving...' : 'Save'}
                            </Button>
                        </div>
                    </>
                )}
            </div>
        </Modal>
    );
}

// ─── Add Action Modal ────────────────────────────────────────────────────────
interface AddActionModalProps {
    isOpen: boolean;
    onClose: () => void;
    defaultDay: number;
    currentWeek: number;
    onScheduled: () => void;
}

function AddActionModal({ isOpen, onClose, defaultDay, currentWeek, onScheduled }: AddActionModalProps) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [category, setCategory] = useState('custom');
    const [priority, setPriority] = useState('medium');
    const [week, setWeek] = useState(currentWeek);
    const [day, setDay] = useState(defaultDay);
    const [isRecurring, setIsRecurring] = useState(false);
    const [recurrenceWeeks, setRecurrenceWeeks] = useState(1);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setDay(defaultDay);
        setWeek(currentWeek);
    }, [defaultDay, currentWeek]);

    const handleSubmit = async () => {
        if (!title.trim()) {
            toast.error('Title required');
            return;
        }
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/calendar/p1/schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title, description, category, priority, week, day,
                    is_recurring: isRecurring,
                    recurrence_weeks: isRecurring ? recurrenceWeeks : 0,
                }),
            });
            if (response.ok) {
                toast.success(`Scheduled: ${title}`);
                setTitle('');
                setDescription('');
                onScheduled();
            } else {
                const err = await response.json();
                toast.error(err.detail || 'Failed');
            }
        } catch {
            toast.error('Error scheduling');
        }
        setLoading(false);
    };

    return (
        <Modal open={isOpen} onOpenChange={(open) => !open && onClose()} title="Schedule Action">
            <div className="space-y-3">
                <div>
                    <label className="block text-xs text-slate-400 mb-1">Title *</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="w-full px-2 py-1.5 text-sm rounded bg-white/10 border border-white/20 text-white placeholder-slate-500"
                        placeholder="Action title..."
                    />
                </div>

                <div>
                    <label className="block text-xs text-slate-400 mb-1">Description</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="w-full px-2 py-1.5 text-sm rounded bg-white/10 border border-white/20 text-white placeholder-slate-500 resize-none"
                        rows={2}
                        placeholder="Details..."
                    />
                </div>

                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-xs text-slate-400 mb-1">Category</label>
                        <select value={category} onChange={(e) => setCategory(e.target.value)}
                            className="w-full px-2 py-1.5 text-sm rounded bg-slate-700 border border-white/20 text-white">
                            <option value="payment">Payment</option>
                            <option value="supply_order">Supply Order</option>
                            <option value="maintenance">Maintenance</option>
                            <option value="marketing">Marketing</option>
                            <option value="negotiation">Negotiation</option>
                            <option value="custom">Custom</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs text-slate-400 mb-1">Priority</label>
                        <select value={priority} onChange={(e) => setPriority(e.target.value)}
                            className="w-full px-2 py-1.5 text-sm rounded bg-slate-700 border border-white/20 text-white">
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-xs text-slate-400 mb-1">Week</label>
                        <input type="number" value={week} onChange={(e) => setWeek(parseInt(e.target.value) || currentWeek)} min={1}
                            className="w-full px-2 py-1.5 text-sm rounded bg-white/10 border border-white/20 text-white" />
                    </div>
                    <div>
                        <label className="block text-xs text-slate-400 mb-1">Day</label>
                        <select value={day} onChange={(e) => setDay(parseInt(e.target.value))}
                            className="w-full px-2 py-1.5 text-sm rounded bg-slate-700 border border-white/20 text-white">
                            {DAY_NAMES.map((name, i) => <option key={name} value={i + 1}>{name}</option>)}
                        </select>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <input type="checkbox" id="add-recurring" checked={isRecurring} onChange={(e) => setIsRecurring(e.target.checked)} />
                    <label htmlFor="add-recurring" className="text-xs text-slate-300">Recurring</label>
                    {isRecurring && (
                        <div className="flex items-center gap-1 ml-2">
                            <span className="text-xs text-slate-400">every</span>
                            <input type="number" value={recurrenceWeeks} onChange={(e) => setRecurrenceWeeks(Math.max(1, parseInt(e.target.value) || 1))}
                                min={1} max={52} className="w-12 px-1 py-0.5 text-xs rounded bg-white/10 border border-white/20 text-white" />
                            <span className="text-xs text-slate-400">weeks</span>
                        </div>
                    )}
                </div>

                <div className="flex gap-2 pt-1">
                    <Button variant="secondary" className="flex-1" onClick={onClose}>Cancel</Button>
                    <Button variant="primary" className="flex-1" onClick={handleSubmit} disabled={loading}>
                        {loading ? 'Saving...' : 'Schedule'}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
