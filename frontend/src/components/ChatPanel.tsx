import React, { useState } from 'react';

interface ChatProps {
  onGeoDataReceived: (geoJson: any) => void;
}

interface Message {
  sender: 'user' | 'agent';
  text: string;
}

export const ChatPanel: React.FC<ChatProps> = ({ onGeoDataReceived }) => {
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'agent', text: 'Hello! I am your Spatial AI Assistant. Ask me anything like "Find properties within 5km of London Eye".' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userText = input;
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText }),
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, { sender: 'agent', text: data.response }]);

      if (data.is_geo_query && data.geojson) {
        onGeoDataReceived(data.geojson);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'agent', text: 'Failed to communicate with GeoAgentic engine backend.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-4 text-slate-100">
      <div className="border-b border-slate-800 pb-3 mb-4">
        <h2 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
          GeoAgentic Copilot
        </h2>
        <p className="text-xs text-slate-400">Natural Language Spatial Intelligence</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-2">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${
              m.sender === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-800 border border-slate-700 text-slate-200'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-xs text-slate-400 animate-pulse">
              Querying PostGIS & RAG Engine...
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-100"
          placeholder="Ask spatial query..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-xl text-sm font-medium transition-all duration-200 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
};