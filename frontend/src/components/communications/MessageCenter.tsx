import { useState, useEffect } from 'react';
import {
  Mail,
  Inbox,
  Send,
  AlertTriangle,
  Clock,
  CheckCircle,
  Filter,
  Users,
  Store,
  Bot,
  Handshake,
  Loader2,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge, Button, TabGroup, TabContent, Modal, ModalFooter } from '../shared';
import type { Message } from '../../types';
import { toast } from 'sonner';

// ═══════════════════════════════════════════════════════════════════════
// MessageCenter Component
// Unified inbox: messages, tickets, masked ethical dilemmas
// ═══════════════════════════════════════════════════════════════════════

const tabs = [
  { id: 'inbox', label: 'Inbox', icon: <Inbox className="w-4 h-4" /> },
  { id: 'tickets', label: 'Tickets', icon: <AlertTriangle className="w-4 h-4" /> },
  { id: 'sent', label: 'Sent', icon: <Send className="w-4 h-4" /> },
  { id: 'contacts', label: 'Contacts', icon: <Users className="w-4 h-4" /> },
];

const intentStyles: Record<string, { variant: 'default' | 'success' | 'warning' | 'danger' | 'info'; label: string }> = {
  chat: { variant: 'default', label: 'Message' },
  proposal: { variant: 'info', label: 'Proposal' },
  negotiation: { variant: 'warning', label: 'Negotiation' },
  dilemma: { variant: 'danger', label: 'Urgent' },
  announcement: { variant: 'success', label: 'Announcement' },
  warning: { variant: 'danger', label: 'Warning' },
  info: { variant: 'info', label: 'Info' },
  dilemma_outcome: { variant: 'default', label: 'Outcome' },
};

export default function MessageCenter() {
  const { getMessages, getPlayerLaundromat, sendMessage, isLoading, getVendors, getCompetitors } = useGameStore();
  const messages = getMessages();
  const laundromat = getPlayerLaundromat();
  const vendors = getVendors();
  const competitors = getCompetitors();
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [composeOpen, setComposeOpen] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const [negotiateVendorId, setNegotiateVendorId] = useState<string | null>(null);

  // Filter messages for inbox (received) vs sent
  const inboxMessages = messages.filter((m) => m.recipient_id === laundromat?.id);
  const sentMessages = messages.filter((m) => m.sender_id === laundromat?.id);

  // Get tickets from laundromat
  const tickets = laundromat?.tickets ?? [];

  // Filter by intent
  const filteredInbox =
    filter === 'all' ? inboxMessages : inboxMessages.filter((m) => m.intent === filter);

  // Build contacts list
  const contacts: { id: string; name: string; type: 'vendor' | 'agent' | 'staff' }[] = [
    ...vendors.map((v) => ({ id: v.id, name: v.name, type: 'vendor' as const })),
    ...competitors.map((c) => ({ id: c.id, name: c.name, type: 'agent' as const })),
    { id: 'game_master', name: 'Game Master', type: 'agent' as const },
  ];

  const handleSendMessage = async (content: string, recipientId: string) => {
    await sendMessage('dm', recipientId, content, 'chat');
    setComposeOpen(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <Mail className="w-6 h-6 text-emerald-400" />
          Message Center
        </h2>
        <Button variant="primary" size="sm" onClick={() => setComposeOpen(true)}>
          <Send className="w-4 h-4" />
          Compose
        </Button>
      </div>

      <TabGroup
        tabs={tabs.map((t) => ({
          ...t,
          badge:
            t.id === 'inbox'
              ? inboxMessages.filter((m) => !m.is_read).length
              : t.id === 'tickets'
                ? tickets.filter((t) => t.status === 'open').length
                : undefined,
        }))}
        defaultValue="inbox"
      >
        {/* Inbox Tab */}
        <TabContent value="inbox">
          {/* Filter Bar */}
          <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
            {['all', 'chat', 'proposal', 'dilemma', 'warning'].map((f) => (
              <Button
                key={f}
                variant={filter === f ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setFilter(f)}
              >
                <Filter className="w-3 h-3" />
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </Button>
            ))}
          </div>

          {/* Message List */}
          <div className="space-y-2">
            {filteredInbox.length > 0 ? (
              filteredInbox.map((message) => (
                <MessageRow
                  key={message.id}
                  message={message}
                  onClick={() => setSelectedMessage(message)}
                />
              ))
            ) : (
              <Card variant="outline" className="text-center py-8">
                <p className="text-slate-500">No messages in inbox.</p>
              </Card>
            )}
          </div>
        </TabContent>

        {/* Tickets Tab */}
        <TabContent value="tickets">
          <div className="space-y-2">
            {tickets.length > 0 ? (
              tickets.map((ticket) => (
                <Card
                  key={ticket.id}
                  variant={ticket.status === 'open' ? 'outline' : 'glass'}
                  className="cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge
                          variant={
                            ticket.severity === 'high'
                              ? 'danger'
                              : ticket.severity === 'medium'
                                ? 'warning'
                                : 'default'
                          }
                        >
                          {ticket.severity}
                        </Badge>
                        <span className="text-sm font-medium text-white">{ticket.type}</span>
                      </div>
                      <p className="text-sm text-slate-400">{ticket.description}</p>
                    </div>
                    <Badge variant={ticket.status === 'open' ? 'warning' : 'success'}>
                      {ticket.status === 'open' ? (
                        <>
                          <Clock className="w-3 h-3" />
                          Open
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-3 h-3" />
                          Resolved
                        </>
                      )}
                    </Badge>
                  </div>
                </Card>
              ))
            ) : (
              <Card variant="outline" className="text-center py-8">
                <p className="text-slate-500">No tickets.</p>
              </Card>
            )}
          </div>
        </TabContent>

        {/* Sent Tab */}
        <TabContent value="sent">
          <div className="space-y-2">
            {sentMessages.length > 0 ? (
              sentMessages.map((message) => (
                <MessageRow
                  key={message.id}
                  message={message}
                  onClick={() => setSelectedMessage(message)}
                />
              ))
            ) : (
              <Card variant="outline" className="text-center py-8">
                <p className="text-slate-500">No sent messages.</p>
              </Card>
            )}
          </div>
        </TabContent>

        {/* Contacts Tab */}
        <TabContent value="contacts">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {contacts.map((contact) => (
              <Card
                key={contact.id}
                variant="glass"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${contact.type === 'vendor' ? 'bg-amber-500/20 text-amber-400' :
                    contact.type === 'agent' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-emerald-500/20 text-emerald-400'
                    }`}>
                    {contact.type === 'vendor' ? <Store className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white">{contact.name}</p>
                    <p className="text-xs text-slate-400 capitalize">{contact.type}</p>
                  </div>
                  <div className="flex gap-2">
                    {contact.type === 'vendor' && (
                      <Button variant="secondary" size="sm" onClick={() => setNegotiateVendorId(contact.id)} title="Negotiate Prices">
                        <Handshake className="w-4 h-4" />
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => setComposeOpen(true)} title="Send Message">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabContent>
      </TabGroup>

      {/* Message Detail Modal */}
      <Modal
        open={!!selectedMessage}
        onOpenChange={() => setSelectedMessage(null)}
        title={`Message from ${selectedMessage?.sender_id}`}
        size="md"
      >
        {selectedMessage && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant={intentStyles[selectedMessage.intent]?.variant ?? 'default'}>
                {intentStyles[selectedMessage.intent]?.label ?? selectedMessage.intent}
              </Badge>
              <span className="text-xs text-slate-400">
                Week {selectedMessage.week}, Day {selectedMessage.day}
              </span>
            </div>
            <p className="text-slate-200 leading-relaxed">{selectedMessage.content}</p>
            <ModalFooter>
              <Button variant="ghost" onClick={() => setSelectedMessage(null)}>
                Close
              </Button>
              <Button variant="primary">Reply</Button>
            </ModalFooter>
          </div>
        )}
      </Modal>

      {/* Compose Modal */}
      <ComposeModal
        open={composeOpen}
        onClose={() => setComposeOpen(false)}
        onSend={handleSendMessage}
        loading={isLoading}
        contacts={contacts}
      />

      {/* Negotiate Modal */}
      <NegotiateModal
        vendorId={negotiateVendorId}
        onClose={() => setNegotiateVendorId(null)}
      />
    </div>
  );
}

// ─── Message Row Component ──────────────────────────────────────────────
function MessageRow({ message, onClick }: { message: Message; onClick: () => void }) {
  const style = intentStyles[message.intent] ?? { variant: 'default', label: 'Message' };

  return (
    <Card
      variant={message.is_read ? 'glass' : 'outline'}
      hover
      className="cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {!message.is_read && <span className="w-2 h-2 rounded-full bg-emerald-400" />}
            <span className="text-sm font-medium text-white truncate">{message.sender_id}</span>
            <Badge variant={style.variant} size="sm">
              {style.label}
            </Badge>
          </div>
          <p className="text-sm text-slate-400 line-clamp-2">{message.content}</p>
        </div>
        <div className="text-xs text-slate-500 whitespace-nowrap">
          W{message.week} D{message.day}
        </div>
      </div>
    </Card>
  );
}

// ─── Compose Modal Component ────────────────────────────────────────────
function ComposeModal({
  open,
  onClose,
  onSend,
  loading,
  contacts,
}: {
  open: boolean;
  onClose: () => void;
  onSend: (content: string, recipientId: string) => void;
  loading: boolean;
  contacts: { id: string; name: string; type: string }[];
}) {
  const [content, setContent] = useState('');
  const [recipient, setRecipient] = useState('');

  const handleSubmit = () => {
    if (content.trim() && recipient.trim()) {
      onSend(content, recipient);
      setContent('');
      setRecipient('');
    }
  };

  return (
    <Modal open={open} onOpenChange={onClose} title="Compose Message" size="md">
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-slate-400 mb-1">To:</label>
          <select
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="">Select recipient...</option>
            {contacts.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.type})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1">Message:</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your message..."
            rows={4}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
          />
        </div>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={loading}
            disabled={!content.trim() || !recipient.trim()}
          >
            <Send className="w-4 h-4" />
            Send
          </Button>
        </ModalFooter>
      </div>
    </Modal>
  );
}

// ─── Negotiate Modal Component (Chat-Based with GM Roleplay) ────────────
interface ChatMessage {
  sender: 'player' | 'vendor';
  text: string;
  offeredPrice?: number;
  accepted?: boolean;
}

function NegotiateModal({
  vendorId,
  onClose,
}: {
  vendorId: string | null;
  onClose: () => void;
}) {
  const [item, setItem] = useState('detergent');
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [dealReached, setDealReached] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  const items = ['detergent', 'softener', 'bleach', 'parts', 'bags'];

  // Load conversation history when modal opens or item changes
  useEffect(() => {
    if (!vendorId) {
      setChatLog([]);
      setHistoryLoaded(false);
      return;
    }

    const loadHistory = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/negotiate/history/${vendorId}/p1?item=${item}`
        );
        if (response.ok) {
          const data = await response.json();
          const existingMessages: ChatMessage[] = data.history.map((h: Record<string, unknown>) => ({
            sender: h.role === 'player' ? 'player' : 'vendor',
            text: h.message as string,
            offeredPrice: h.offered_price as number | undefined,
            accepted: h.accepted as boolean | undefined,
          }));
          setChatLog(existingMessages);
          // Check if there's already an accepted deal
          const accepted = existingMessages.some((m) => m.accepted);
          setDealReached(accepted);
        }
      } catch (err) {
        console.error('Failed to load negotiation history:', err);
      }
      setHistoryLoaded(true);
    };

    loadHistory();
  }, [vendorId, item]);


  const handleSendMessage = async () => {
    if (!vendorId || !inputMessage.trim() || loading) return;

    const playerMsg = inputMessage.trim();
    setChatLog((prev) => [...prev, { sender: 'player', text: playerMsg }]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/negotiate/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: 'p1',
          vendor_id: vendorId,
          item: item,
          message: playerMsg,
        }),
      });

      if (!response.ok) throw new Error('Negotiation failed');
      const data = await response.json();

      setChatLog((prev) => [
        ...prev,
        {
          sender: 'vendor',
          text: data.vendor_response,
          offeredPrice: data.offered_price,
          accepted: data.accepted,
        },
      ]);

      if (data.accepted) {
        setDealReached(true);
        toast.success(`Deal reached! Price: $${data.offered_price}`);
      }
    } catch (err) {
      setChatLog((prev) => [...prev, { sender: 'vendor', text: 'Sorry, I am unable to respond right now.' }]);
      toast.error('Negotiation error');
    }
    setLoading(false);
  };

  const handleClose = () => {
    setChatLog([]);
    setDealReached(false);
    onClose();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!vendorId) return null;

  return (
    <Modal open={!!vendorId} onOpenChange={handleClose} title="Negotiate with Vendor" size="md">
      <div className="space-y-4">
        {/* Item Selector */}
        <div>
          <label className="block text-sm text-slate-400 mb-1">Negotiating:</label>
          <select
            value={item}
            onChange={(e) => setItem(e.target.value)}
            disabled={chatLog.length > 0}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
          >
            {items.map((i) => (
              <option key={i} value={i}>{i.charAt(0).toUpperCase() + i.slice(1)}</option>
            ))}
          </select>
        </div>

        {/* Chat Log */}
        <div className="h-64 overflow-y-auto bg-slate-800/50 rounded-lg p-3 space-y-2">
          {!historyLoaded ? (
            <div className="flex h-full items-center justify-center">
              <Loader2 className="w-6 h-6 animate-spin text-slate-500" />
            </div>
          ) : chatLog.length === 0 ? (
            <p className="text-slate-500 text-sm text-center py-8">
              Start negotiating by sending a message...
            </p>
          ) : (
            chatLog.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.sender === 'player' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-lg ${msg.sender === 'player'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'bg-slate-700 text-slate-200'
                    }`}
                >
                  <p className="text-sm">{msg.text}</p>
                  {msg.offeredPrice && (
                    <p className="text-xs mt-1 text-amber-400">
                      Offered Price: ${msg.offeredPrice}
                    </p>
                  )}
                  {msg.accepted && (
                    <span className="inline-block mt-1 text-xs bg-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded">
                      Deal Accepted!
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Input */}
        {!dealReached && (
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your negotiation message..."
              className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <Button variant="primary" onClick={handleSendMessage} loading={loading}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
        )}

        <ModalFooter>
          <Button variant="ghost" onClick={handleClose}>
            {dealReached ? 'Done' : 'Cancel'}
          </Button>
          {dealReached && (
            <Button variant="primary" onClick={handleClose}>
              <Handshake className="w-4 h-4" />
              Accept Deal
            </Button>
          )}
        </ModalFooter>
      </div>
    </Modal>
  );
}
