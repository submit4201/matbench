import { useState } from 'react';
import {
  Mail,
  Inbox,
  Send,
  AlertTriangle,
  Clock,
  CheckCircle,
  Filter,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge, Button, TabGroup, TabContent, Modal, ModalFooter } from '../shared';
import type { Message } from '../../types';

// ═══════════════════════════════════════════════════════════════════════
// MessageCenter Component
// Unified inbox: messages, tickets, masked ethical dilemmas
// ═══════════════════════════════════════════════════════════════════════

const tabs = [
  { id: 'inbox', label: 'Inbox', icon: <Inbox className="w-4 h-4" /> },
  { id: 'tickets', label: 'Tickets', icon: <AlertTriangle className="w-4 h-4" /> },
  { id: 'sent', label: 'Sent', icon: <Send className="w-4 h-4" /> },
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
  const { getMessages, getPlayerLaundromat, sendMessage, isLoading } = useGameStore();
  const messages = getMessages();
  const laundromat = getPlayerLaundromat();
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [composeOpen, setComposeOpen] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  // Filter messages for inbox (received) vs sent
  const inboxMessages = messages.filter((m) => m.recipient_id === laundromat?.id);
  const sentMessages = messages.filter((m) => m.sender_id === laundromat?.id);

  // Get tickets from laundromat
  const tickets = laundromat?.tickets ?? [];

  // Filter by intent
  const filteredInbox =
    filter === 'all' ? inboxMessages : inboxMessages.filter((m) => m.intent === filter);

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
}: {
  open: boolean;
  onClose: () => void;
  onSend: (content: string, recipientId: string) => void;
  loading: boolean;
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
          <input
            type="text"
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            placeholder="Recipient ID (e.g., ai_1)"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
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
