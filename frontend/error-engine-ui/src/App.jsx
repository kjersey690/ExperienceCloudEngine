import React, { useState } from 'react';
import { Search, ShieldAlert, Zap, PlusCircle, ThumbsUp, ThumbsDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('search');
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ 
    name: '', 
    category: 'ExperienceBundle', 
    resolution: '', 
    replication_steps: '' 
  });

  const handleSearch = async (query) => {
    if (query.length < 3) { setResults([]); return; }
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
      setResults(res.data);
    } catch (err) { console.error("Search failed", err); }
    finally { setLoading(false); }
  };

  const handleVote = async (id, change) => {
    setResults(prev => prev.map(item => 
      item.id === id ? { ...item, votes: (item.votes || 0) + change } : item
    ));
    try {
      await axios.post(`${API_BASE}/vote`, { entry_id: id, change: change });
    } catch (err) { console.error("Vote failed", err); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/contribute`, form);
      setSubmitted(true);
      setTimeout(() => {
        setForm({ name: '', category: 'ExperienceBundle', resolution: '', replication_steps: '' });
        setSubmitted(false);
        setActiveTab('search');
      }, 3000);
    } catch (err) { console.error("Submission failed", err); }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-blue-500/30">
      <header className="border-b border-slate-800/60 bg-slate-900/20 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-500/20">
              <ShieldAlert className="text-white w-6 h-6" />
            </div>
<h1 className="text-xl font-bold tracking-tight uppercase italic flex items-center gap-2">
  {/* Light Silver/White for EXBUNDLE */}
  <span className="text-slate-100 drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]">
    ExBundle
  </span>
  
  {/* Glowing Cyan for ENGINE */}
  <span className="text-cyan-400 font-black tracking-widest text-2xl drop-shadow-[0_0_12px_rgba(34,211,238,0.8)]">
    Engine
  </span>
</h1>
          </div>
          <nav className="flex gap-6 text-sm font-medium">
            <button 
              onClick={() => setActiveTab('search')}
              className={`${activeTab === 'search' ? 'text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:text-white'} pb-1 transition-all`}
            >
              Search
            </button>
            <button 
              onClick={() => setActiveTab('contribute')}
              className={`${activeTab === 'contribute' ? 'text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:text-white'} pb-1 transition-all flex items-center gap-1`}
            >
              <PlusCircle className="w-4 h-4" /> Contribute
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {activeTab === 'search' ? (
            <motion.div key="search-tab" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="text-center mb-16">
                <h2 className="text-4xl font-extrabold mb-4 tracking-tight">
                <span className="text-slate-100">Experience Cloud</span>{" "}
                <span className="text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.3)]">
                Diagnostics.
                </span>
                </h2>
                <div className="max-w-3xl mx-auto relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-1000"></div>
                  <div className="relative">
                    <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400" />
                    <input 
                      type="text"
                      onChange={(e) => handleSearch(e.target.value)}
                      placeholder="Paste deployment error..."
                      className="w-full bg-slate-900/80 border border-slate-700/50 p-5 pl-14 rounded-xl focus:ring-1 focus:ring-blue-500 outline-none text-white transition-all"
                    />
                    {loading && <div className="absolute right-5 top-1/2 -translate-y-1/2 animate-spin text-blue-500"><Zap className="w-5 h-5" /></div>}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 items-stretch">
                {results.map((item, index) => (
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    key={item.id} 
                    className="group flex flex-col h-full bg-slate-900/40 border border-slate-800 hover:border-blue-500/40 rounded-2xl p-6 transition-all"
                  >
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex flex-col gap-2">
                        <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase border border-blue-500/20 w-fit">
                          {item.metadata.category}
                        </span>
                        <div className="flex flex-col">
                          <span className="text-[9px] text-slate-500 uppercase font-mono tracking-widest">Confidence</span>
                          <span className="text-sm font-bold text-blue-400 font-mono">
                            {(item.score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 bg-slate-950/80 px-3 py-1.5 rounded-full border border-slate-800 shadow-lg">
                        <button onClick={() => handleVote(item.id, 1)} className="text-slate-500 hover:text-green-500 transition-colors"><ThumbsUp className="w-3.5 h-3.5" /></button>
                        <span className="text-xs font-bold text-slate-300 min-w-[12px] text-center">{item.votes || 0}</span>
                        <button onClick={() => handleVote(item.id, -1)} className="text-slate-500 hover:text-red-500 transition-colors"><ThumbsDown className="w-3.5 h-3.5" /></button>
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-3 group-hover:text-blue-400 transition-colors">{item.metadata.error_name}</h3>
                    <div className="flex-grow bg-slate-950/50 rounded-lg p-4 border border-slate-800/50">
                      <p className="text-slate-400 text-sm leading-relaxed italic">"{item.metadata.resolution_steps || item.metadata.resolution}"</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div key="contribute-tab" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} className="max-w-2xl mx-auto">
              <div className="bg-slate-900/40 border border-slate-800 p-8 rounded-2xl backdrop-blur-sm">
                <AnimatePresence mode="wait">
                  {!submitted ? (
                    <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                        <PlusCircle className="text-blue-500" /> Contribute to Engine
                      </h2>
                      <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                          <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Error Signature</label>
                          <input className="w-full bg-slate-950 border border-slate-700 p-3 rounded-lg focus:ring-1 focus:ring-blue-500 outline-none" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Replication Steps</label>
                          <textarea rows="2" className="w-full bg-slate-950 border border-slate-700 p-3 rounded-lg focus:ring-1 focus:ring-blue-500 outline-none" value={form.replication_steps} onChange={e => setForm({...form, replication_steps: e.target.value})} />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Resolution</label>
                          <textarea rows="4" className="w-full bg-slate-950 border border-slate-700 p-3 rounded-lg focus:ring-1 focus:ring-blue-500 outline-none" value={form.resolution} onChange={e => setForm({...form, resolution: e.target.value})} required />
                        </div>
                        <button type="submit" className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-all shadow-lg shadow-blue-500/20 uppercase tracking-widest text-xs">Transmit to Engine</button>
                      </form>
                    </motion.div>
                  ) : (
                    <motion.div key="success" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center py-10">
                      <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500/20 rounded-full mb-6 border border-blue-500/50"><Zap className="text-blue-500 w-8 h-8" /></div>
                      <h2 className="text-2xl font-bold text-white mb-2 uppercase italic tracking-tighter">Transmission Successful</h2>
                      <p className="text-slate-400 text-sm">Engine intelligence updated. Redirecting...</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}