import React, { useState } from 'react';
import { 
  Mail, Globe, AlertTriangle, User, Shield, Send, 
  MessageSquare, CheckCircle, Megaphone,
  Zap, Clock, FileText
} from 'lucide-react';
import type { Message, Ticket } from '../types';

interface MessageCenterProps {
  messages: Message[];
  tickets: Ticket[];
  currentWeek: number;
  competitors: { id: string; name: string }[];
  onResolveDilemma: (choiceId: string) => void;
  onResolveTicket: (ticketId: string) => void;
  onSendMessage: (channel: string, recipientId: string, content: string, intent: string) => void;
}

type TabType = 'inbox' | 'news' | 'tickets' | 'compose';

const MessageCenter: React.FC<MessageCenterProps> = ({ 
  messages, 
  tickets,
  currentWeek, 
  competitors,
  onResolveDilemma,
  onResolveTicket,
  onSendMessage
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('inbox');
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  
  // Compose state
  const [composeChannel, setComposeChannel] = useState<'dm' | 'public' | 'formal'>('dm');
  const [composeRecipient, setComposeRecipient] = useState('');
  const [composeContent, setComposeContent] = useState('');
  const [composeIntent, setComposeIntent] = useState('chat');

  // Filter messages
  const inboxMessages = messages.filter(m => 
    m.channel === 'dm' || 
    m.channel === 'formal' || 
    (m.channel === 'system' && m.intent !== 'announcement') // Include dilemmas in inbox
  );
  
  const newsMessages = messages.filter(m => 
    m.channel === 'public' || 
    (m.channel === 'system' && m.intent === 'announcement')
  );

  const openTickets = tickets.filter(t => t.status === 'open');

  const getFilteredMessages = () => {
    switch (activeTab) {
      case 'inbox': return inboxMessages;
      case 'news': return newsMessages;
      default: return [];
    }
  };

  const getSenderIcon = (senderId: string, channel: string) => {
    if (senderId === 'SYSTEM' || senderId === 'GAME_MASTER') return <Shield size={20} className="text-gray-500" />; // Neutral color
    if (senderId === 'REGULATOR') return <AlertTriangle size={20} className="text-red-500" />;
    if (channel === 'public') return <Globe size={20} className="text-blue-500" />;
    return <User size={20} className="text-emerald-500" />;
  };

  const getIntentBadge = (intent: string) => {
    const styles: Record<string, string> = {
      chat: 'bg-gray-100 text-gray-600',
      proposal: 'bg-blue-100 text-blue-700',
      negotiation: 'bg-emerald-100 text-emerald-700',
      // Camouflage dilemma as urgent/warning
      dilemma: 'bg-amber-100 text-amber-800', 
      dilemma_outcome: 'bg-gray-100 text-gray-700',
      warning: 'bg-red-100 text-red-700',
      announcement: 'bg-orange-100 text-orange-700',
      info: 'bg-sky-100 text-sky-700'
    };
    return styles[intent] || styles.chat;
  };

  const getIntentLabel = (intent: string) => {
    if (intent === 'dilemma') return 'Action Required';
    if (intent === 'dilemma_outcome') return 'Update';
    return intent;
  };

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'high': return {
        bg: 'bg-gradient-to-r from-red-50 to-rose-50',
        border: 'border-red-300',
        badge: 'bg-red-500 text-white',
        icon: <AlertTriangle size={14} />,
      };
      case 'medium': return {
        bg: 'bg-gradient-to-r from-amber-50 to-yellow-50',
        border: 'border-amber-300',
        badge: 'bg-amber-500 text-white',
        icon: <Clock size={14} />,
      };
      default: return {
        bg: 'bg-gradient-to-r from-blue-50 to-indigo-50',
        border: 'border-blue-300',
        badge: 'bg-blue-500 text-white',
        icon: <Shield size={14} />,
      };
    }
  };

  const handleSend = () => {
    if (!composeContent.trim()) return;
    const recipient = composeChannel === 'public' ? 'ALL' : composeRecipient;
    onSendMessage(composeChannel, recipient, composeContent, composeIntent);
    setComposeContent('');
    setActiveTab('inbox');
  };

  const tabConfig = [
    { id: 'inbox' as TabType, label: 'Inbox', icon: Mail, count: inboxMessages.filter(m => !m.is_read).length, color: 'indigo' },
    { id: 'news' as TabType, label: 'News', icon: Globe, count: 0, color: 'blue' },
    { id: 'tickets' as TabType, label: 'Tickets', icon: MessageSquare, count: openTickets.length, color: 'orange' },
    // Removed explicit Ethics Tab
    { id: 'compose' as TabType, label: 'Compose', icon: Send, count: 0, color: 'emerald' },
  ];

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 flex-shrink-0">
        <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
          <Mail className="text-white" size={24} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Comm Hub</h2>
          <div className="flex gap-4 text-sm text-gray-500 font-medium">
            <span>Inbox: {inboxMessages.filter(m => !m.is_read).length} new</span>
            <span>•</span>
            <span>Tickets: {openTickets.length} open</span>
            <span>•</span>
            <span>Week {currentWeek}</span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden flex min-h-0">
        
        {/* Sidebar */}
        <div className="w-1/3 border-r border-gray-100 flex flex-col bg-gray-50/50">
          {/* Tabs */}
          <div className="p-2 flex flex-wrap gap-1 border-b border-gray-100 bg-white">
            {tabConfig.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold transition-all ${
                  activeTab === tab.id 
                    ? `bg-${tab.color}-100 text-${tab.color}-700 shadow-sm` 
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                <tab.icon size={14} />
                {tab.label}
                {tab.count > 0 && (
                  <span className={`ml-1 px-1.5 py-0.5 rounded-full text-[10px] bg-${tab.color}-500 text-white`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Content based on tab */}
          <div className="flex-1 overflow-y-auto">
            {/* Messages List (Inbox, News) */}
            {(activeTab === 'inbox' || activeTab === 'news') && (
              <>
                {getFilteredMessages().length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Mail size={32} className="mx-auto mb-2 opacity-30" />
                    <p>No messages</p>
                  </div>
                ) : (
                  getFilteredMessages().sort((a,b) => (b.week * 7 + b.day) - (a.week * 7 + a.day)).map(msg => (
                    <div
                      key={msg.id}
                      onClick={() => setSelectedMessage(msg)}
                      className={`p-4 border-b border-gray-100 cursor-pointer transition-colors hover:bg-white ${
                        selectedMessage?.id === msg.id ? 'bg-white border-l-4 border-l-indigo-500 shadow-sm' : 'border-l-4 border-l-transparent'
                      } ${!msg.is_read ? 'bg-indigo-50/30' : ''}`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-bold text-gray-800 text-sm truncate">{msg.sender_id}</span>
                        <span className="text-xs text-gray-400 whitespace-nowrap">W{msg.week} D{msg.day}</span>
                      </div>
                      <p className="text-xs font-bold uppercase mb-1">
                        <span className={`px-1.5 py-0.5 rounded ${getIntentBadge(msg.intent)}`}>
                          {getIntentLabel(msg.intent)}
                        </span>
                      </p>
                      <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed">
                        {msg.content}
                      </p>
                    </div>
                  ))
                )}
              </>
            )}

            {/* Tickets List */}
            {activeTab === 'tickets' && (
              <div className="p-4 space-y-3">
                {openTickets.length > 0 && (
                  <button
                    onClick={() => openTickets.forEach(t => onResolveTicket(t.id))}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-lg font-bold shadow-sm hover:shadow-md transition-all"
                  >
                    <Zap size={16} />
                    Resolve All ({openTickets.length})
                  </button>
                )}
                
                {tickets.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <CheckCircle size={32} className="mx-auto mb-2 text-emerald-200" />
                    <p className="font-bold text-gray-600">All Clear!</p>
                    <p className="text-sm">No tickets</p>
                  </div>
                ) : (
                  tickets.map(ticket => {
                    const config = getSeverityConfig(ticket.severity || 'low');
                    const isResolved = ticket.status === 'resolved';
                    
                    return (
                      <div 
                        key={ticket.id} 
                        className={`group p-3 rounded-lg border-2 transition-all ${
                          isResolved 
                            ? 'bg-gray-50 border-gray-200 opacity-60' 
                            : `${config.bg} ${config.border}`
                        }`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${
                              isResolved ? 'bg-gray-200 text-gray-500' : config.badge
                            }`}>
                              {isResolved ? <CheckCircle size={12} /> : config.icon}
                              {ticket.severity?.toUpperCase() || 'LOW'}
                            </span>
                            <span className="font-bold text-gray-900 text-sm">{ticket.type}</span>
                          </div>
                          
                          {!isResolved && (
                            <button 
                              onClick={() => onResolveTicket(ticket.id)}
                              className="flex items-center gap-1 px-2 py-1 bg-white text-emerald-600 hover:bg-emerald-500 hover:text-white rounded-lg shadow-sm font-bold text-xs transition-all"
                            >
                              <CheckCircle size={12} />
                              Resolve
                            </button>
                          )}
                        </div>
                        <p className="text-gray-700 text-sm">{ticket.description}</p>
                      </div>
                    );
                  })
                )}
              </div>
            )}

            {/* Compose Form */}
            {activeTab === 'compose' && (
              <div className="p-4 space-y-4">
                {/* Channel Selection */}
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Channel</label>
                  <div className="flex gap-2">
                    {[
                      { id: 'dm', label: 'DM', icon: User },
                      { id: 'public', label: 'Public', icon: Megaphone },
                      { id: 'formal', label: 'Proposal', icon: FileText },
                    ].map(ch => (
                      <button
                        key={ch.id}
                        onClick={() => setComposeChannel(ch.id as any)}
                        className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-bold transition-all ${
                          composeChannel === ch.id 
                            ? 'bg-indigo-100 text-indigo-700' 
                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                        }`}
                      >
                        <ch.icon size={14} />
                        {ch.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Recipient (not for public) */}
                {composeChannel !== 'public' && (
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2">To</label>
                    <select
                      value={composeRecipient}
                      onChange={(e) => setComposeRecipient(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    >
                      <option value="">Select recipient...</option>
                      {competitors.map(c => (
                        <option key={c.id} value={c.id}>{c.name} ({c.id})</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Intent */}
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Intent</label>
                  <select
                    value={composeIntent}
                    onChange={(e) => setComposeIntent(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  >
                    <option value="chat">Chat</option>
                    <option value="proposal">Proposal</option>
                    <option value="negotiation">Negotiation</option>
                    <option value="info">Info</option>
                  </select>
                </div>

                {/* Message Content */}
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Message</label>
                  <textarea
                    value={composeContent}
                    onChange={(e) => setComposeContent(e.target.value)}
                    placeholder="Type your message..."
                    rows={5}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none"
                  />
                </div>

                {/* Send Button */}
                <button
                  onClick={handleSend}
                  disabled={!composeContent.trim() || (composeChannel !== 'public' && !composeRecipient)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={18} />
                  Send Message
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Detail View */}
        <div className="flex-1 flex flex-col bg-white">
          {selectedMessage && (activeTab === 'inbox' || activeTab === 'news') ? (
            <>
              {/* Message Header */}
              <div className="p-6 border-b border-gray-100">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                      {getSenderIcon(selectedMessage.sender_id, selectedMessage.channel)}
                    </div>
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">{selectedMessage.sender_id}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span>To: {selectedMessage.recipient_id || 'Public'}</span>
                        <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
                        <span className="uppercase text-xs font-bold tracking-wider">{selectedMessage.channel}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-gray-900">Week {selectedMessage.week}, Day {selectedMessage.day}</div>
                    <div className={`inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${getIntentBadge(selectedMessage.intent)}`}>
                      {getIntentLabel(selectedMessage.intent)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Message Body */}
              <div className="flex-1 p-6 overflow-y-auto">
                <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {selectedMessage.content}
                </div>

                {/* Dilemma Actions - Camouflaged as Actions */}
                {selectedMessage.intent === 'dilemma' && selectedMessage.attachments && (
                  <div className="mt-8 p-4 bg-gray-50 rounded-xl border border-gray-100">
                    <h4 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                       <CheckCircle size={18} className="text-gray-500" /> Response Required
                    </h4>
                    <p className="text-sm text-gray-600 mb-4">Please select a course of action:</p>
                    <div className="flex flex-col gap-3">
                      {selectedMessage.attachments.map((choice: any) => (
                        <button
                          key={choice.id}
                          onClick={() => onResolveDilemma(choice.id)}
                          className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all text-left group"
                        >
                          <div>
                            <span className="block font-bold text-gray-800 group-hover:text-black">{choice.label}</span>
                            <span className="block text-xs text-gray-500 mt-1">{choice.description}</span>
                          </div>
                          {/* Hidden risk tag for 'ethical' obfuscation */}
                          {/* {choice.risk && (
                             <span className="text-xs font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded max-w-[120px] text-right">
                               ⚠ {choice.risk}
                             </span>
                          )} */}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-300">
              <div className="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                {activeTab === 'tickets' ? <MessageSquare size={48} className="opacity-20" /> : <Mail size={48} className="opacity-20" />}
              </div>
              <p className="font-medium text-lg">
                {activeTab === 'tickets' ? 'Select a ticket to view details' : 
                 activeTab === 'compose' ? 'Compose a new message' : 
                 'Select a message to read'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageCenter;
