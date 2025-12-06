import React from 'react';
import { MessageSquare, CheckCircle, AlertTriangle, Clock, Shield, Zap } from 'lucide-react';
import type { Ticket } from '../types';

interface TicketSystemProps {
  tickets: Ticket[];
  onResolve: (id: string) => void;
}

const TicketSystem: React.FC<TicketSystemProps> = ({ tickets, onResolve }) => {
  
  const openTickets = tickets.filter(t => t.status === 'open');
  const resolvedTickets = tickets.filter(t => t.status === 'resolved');

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'high': return {
        bg: 'bg-gradient-to-r from-red-50 to-rose-50',
        border: 'border-red-300',
        badge: 'bg-red-500 text-white',
        icon: <AlertTriangle size={14} />,
        accent: 'text-red-600'
      };
      case 'medium': return {
        bg: 'bg-gradient-to-r from-amber-50 to-yellow-50',
        border: 'border-amber-300',
        badge: 'bg-amber-500 text-white',
        icon: <Clock size={14} />,
        accent: 'text-amber-600'
      };
      default: return {
        bg: 'bg-gradient-to-r from-blue-50 to-indigo-50',
        border: 'border-blue-300',
        badge: 'bg-blue-500 text-white',
        icon: <Shield size={14} />,
        accent: 'text-blue-600'
      };
    }
  };

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg shadow-orange-200">
            <MessageSquare className="text-white" size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Support Tickets</h2>
            <p className="text-sm text-gray-500">{openTickets.length} open • {resolvedTickets.length} resolved</p>
          </div>
        </div>
        
        {openTickets.length > 0 && (
          <button
            onClick={() => openTickets.forEach(t => onResolve(t.id))}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-bold shadow-lg shadow-emerald-200 hover:shadow-xl hover:scale-105 transition-all"
          >
            <Zap size={18} />
            Resolve All ({openTickets.length})
          </button>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-4 flex-shrink-0">
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase mb-1">High Priority</div>
          <div className="text-2xl font-bold text-red-600">{openTickets.filter(t => t.severity === 'high').length}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase mb-1">Medium Priority</div>
          <div className="text-2xl font-bold text-amber-600">{openTickets.filter(t => t.severity === 'medium').length}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase mb-1">Low Priority</div>
          <div className="text-2xl font-bold text-blue-600">{openTickets.filter(t => !t.severity || t.severity === 'low').length}</div>
        </div>
      </div>

      {/* Tickets List */}
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
        <div className="px-5 py-3 border-b border-gray-100 bg-gray-50 flex-shrink-0">
          <span className="font-bold text-gray-700">Active Tickets</span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {tickets.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400">
              <CheckCircle size={48} className="mb-4 text-emerald-200" />
              <p className="text-lg font-bold text-gray-600">All Clear!</p>
              <p className="text-sm">No active tickets. Great work!</p>
            </div>
          ) : (
            tickets.map((ticket) => {
              const config = getSeverityConfig(ticket.severity || 'low');
              const isResolved = ticket.status === 'resolved';
              
              return (
                <div 
                  key={ticket.id} 
                  className={`group p-4 rounded-xl border-2 transition-all duration-300 ${
                    isResolved 
                      ? 'bg-gray-50 border-gray-200 opacity-60' 
                      : `${config.bg} ${config.border} hover:shadow-lg`
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        isResolved ? 'bg-gray-200 text-gray-500' : config.badge
                      }`}>
                        {isResolved ? <CheckCircle size={12} /> : config.icon}
                        {ticket.severity?.toUpperCase() || 'LOW'}
                      </span>
                      <span className="font-bold text-gray-900">{ticket.type}</span>
                    </div>
                    
                    {!isResolved ? (
                      <button 
                        onClick={() => onResolve(ticket.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-emerald-600 hover:bg-emerald-500 hover:text-white rounded-lg shadow-sm font-bold text-sm transition-all opacity-0 group-hover:opacity-100"
                      >
                        <CheckCircle size={14} />
                        Resolve
                      </button>
                    ) : (
                      <span className="flex items-center gap-1 text-xs font-bold text-emerald-600 px-2 py-1 bg-emerald-100 rounded-lg">
                        <CheckCircle size={12} />
                        RESOLVED
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 text-sm leading-relaxed">{ticket.description}</p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default TicketSystem;
