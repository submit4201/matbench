import React from 'react';
import { Users } from 'lucide-react';
import type { Laundromat } from '../../types';

interface StaffWidgetProps {
  laundromat: Laundromat;
}

const StaffWidget: React.FC<StaffWidgetProps> = ({ laundromat }) => {
  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-sm overflow-hidden">
         <div className="bg-gradient-to-r from-cyan-900 to-blue-900 p-5 border-b border-white/10">
           <div className="flex items-center gap-3">
             <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center border border-white/10">
               <Users className="text-white" size={20} />
             </div>
             <div>
               <h3 className="font-bold text-white text-lg">Staff Management</h3>
               <p className="text-cyan-200 text-xs">Manage your employees</p>
             </div>
           </div>
         </div>
         
         <div className="p-5">
           {(!laundromat.staff || laundromat.staff.length === 0) ? (
              <div className="text-center py-8 text-slate-400 bg-slate-900/50 rounded-xl border border-dashed border-slate-700">
                <Users className="mx-auto mb-2 text-slate-500" size={32} />
                <p className="font-medium">No staff hired yet</p>
                <p className="text-sm">Hire staff from the Market tab to automate operations.</p>
              </div>
           ) : (
              <div className="space-y-3">
                {laundromat.staff.map((employee: { name: string; role: string; wage: number }, idx: number) => (
                  <div key={idx} className="p-4 border border-slate-700 bg-slate-700/30 rounded-xl flex justify-between items-center hover:bg-slate-700/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center font-bold text-slate-400 border border-slate-600 shadow-inner">
                        {employee.name?.[0] || 'E'}
                      </div>
                      <div>
                         <div className="font-bold text-white">{employee.name || `Staff #${idx+1}`}</div>
                         <div className="text-xs text-slate-400">{employee.role || 'General Staff'}</div>
                      </div>
                    </div>
                    <div className="text-right">
                       <div className="font-mono font-bold text-slate-300">${employee.wage || 15}/hr</div>
                       <div className="text-xs text-emerald-400 font-bold">Active</div>
                    </div>
                  </div>
                ))}
              </div>
           )}
         </div>
      </div>
    </div>
  );
};

export default StaffWidget;
