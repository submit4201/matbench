import React from 'react';
import type { Laundromat } from '../types';
import StaffWidget from './widgets/StaffWidget';
import { Users, Briefcase } from 'lucide-react';

interface StaffPanelProps {
  laundromat: Laundromat;
}

const StaffPanel: React.FC<StaffPanelProps> = ({ laundromat }) => {
  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 shadow-xl flex-shrink-0">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/5 via-transparent to-transparent"></div>
        </div>
        
        <div className="relative flex items-center gap-4">
          <div className="w-14 h-14 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/30 ring-2 ring-white/20">
            <Users className="text-white" size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Human Resources</h2>
            <p className="text-slate-400 text-sm">Manage staff and hiring</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto min-h-0 bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-4">
        <StaffWidget laundromat={laundromat} />
        
        {/* Placeholder for Hiring Interface if we want to expand it later */}
        <div className="mt-4 p-4 rounded-xl border border-slate-700 bg-slate-900/30 text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-800 mb-2">
                <Briefcase size={20} className="text-slate-500" />
            </div>
            <h3 className="text-slate-300 font-bold">Hiring Portal</h3>
            <p className="text-slate-500 text-sm">Advanced recruitment features coming soon.</p>
        </div>
      </div>
    </div>
  );
};

export default StaffPanel;
