import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Activity, 
  AlertTriangle, 
  Database, 
  Settings, 
  Play, 
  Square, 
  RefreshCw,
  Clock,
  CheckCircle2,
  Lock,
  Cpu,
  BarChart3
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const API_URL = 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState({ 
    live: { packets_processed: 0, intrusions_detected: 0, last_confidence: 0 },
    is_running: false,
    system_status: 'Initializing...'
  });
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isTraining, setIsTraining] = useState(false);

  // Poll for data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await fetch(`${API_URL}/stats`);
        const statsData = await statsRes.json();
        setStats(statsData);

        const logsRes = await fetch(`${API_URL}/logs`);
        const logsData = await logsRes.json();
        setLogs(logsData);
      } catch (err) {
        console.error("API Error", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleSimulation = async () => {
    const endpoint = stats.is_running ? 'stop' : 'start';
    await fetch(`${API_URL}/simulation/${endpoint}`, { method: 'POST' });
  };

  const handleTrain = async () => {
    setIsTraining(true);
    await fetch(`${API_URL}/train`, { method: 'POST' });
    setTimeout(() => setIsTraining(false), 5000); // UI feedback
  };

  // Prepare chart data from logs (sliced to latest 10 items to keep the graph shorter)
  const chartData = logs.slice(0, 10).reverse().map((log, i) => ({
    name: log.timestamp,
    confidence: log.confidence * 100,
    is_alert: log.is_alert ? 100 : 0
  }));

  return (
    <div className="flex h-screen overflow-hidden bg-deep">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-sidebar p-6 flex flex-col gap-8">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-lg shadow-lg shadow-blue-600/30">
            <Shield size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white font-['Outfit']">SentinelNet</h1>
        </div>
        
        <nav className="flex flex-col gap-2 flex-grow">
          <NavItem 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')}
            icon={<BarChart3 size={18}/>} 
            label="Overview" 
          />
          <NavItem 
            active={activeTab === 'live'} 
            onClick={() => setActiveTab('live')}
            icon={<Activity size={18}/>} 
            label="Live Traffic" 
          />
          <NavItem 
            active={activeTab === 'training'} 
            onClick={() => setActiveTab('training')}
            icon={<Cpu size={18}/>} 
            label="AI Models" 
          />
          <NavItem 
            active={activeTab === 'alerts'} 
            onClick={() => setActiveTab('alerts')}
            icon={<AlertTriangle size={18}/>} 
            label="Incidents" 
          />
        </nav>

        <div className="p-4 bg-white/5 rounded-xl border border-white/5 mt-auto">
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${stats.is_running ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-xs font-medium text-slate-400">System Status</span>
          </div>
          <p className="text-sm font-semibold">{stats.system_status}</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8 bg-gradient-glow">
        <header className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-bold text-white mb-1 font-['Outfit']">Network Intelligence</h2>
            <p className="text-slate-400 font-medium">Real-time threat detection and anomaly analytics</p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={handleToggleSimulation}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-full font-bold transition-all shadow-lg active:scale-95 ${
                stats.is_running 
                ? 'bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20' 
                : 'bg-emerald-500 text-white hover:bg-emerald-600 shadow-emerald-500/20'
              }`}
            >
              {stats.is_running ? <Square size={18} fill="currentColor"/> : <Play size={18} fill="currentColor"/>}
              {stats.is_running ? 'Stop Monitor' : 'Start Monitor'}
            </button>
            <button 
              onClick={handleTrain}
              disabled={isTraining}
              className="px-6 py-2.5 rounded-full bg-white/5 border border-white/10 text-white font-bold hover:bg-white/10 transition-all flex items-center gap-2"
            >
              <RefreshCw size={18} className={isTraining ? 'animate-spin' : ''}/>
              Re-Train AI
            </button>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Stats Cards */}
            <StatCard 
              className="col-span-4"
              icon={<Database size={24} className="text-blue-400" />}
              label="Traffic Processed"
              value={stats.live.packets_processed.toLocaleString()}
              subLabel="Live Stream Packets"
            />
            <StatCard 
              className="col-span-4"
              icon={<Shield size={24} className="text-emerald-400" />}
              label="System Security"
              value="Optimum"
              subLabel="AI Model RF_v1.2 Active"
            />
            <StatCard 
              className="col-span-4 border-red-500/20"
              icon={<AlertTriangle size={24} className="text-orange-400" />}
              label="Intrusions Blocked"
              value={stats.live.intrusions_detected}
              subLabel="Detected in Last 24h"
              urgent={stats.live.intrusions_detected > 0}
            />

            {/* Chart Area */}
            <div className="col-span-8 glass p-6 h-[240px]">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-bold font-['Outfit']">Threat Activity Graph</h3>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Confidence Level / Anomaly Score</p>
                </div>
                <div className="flex items-center gap-4">
                     <div className="flex items-center gap-2"><div className="w-3 h-3 bg-blue-500 rounded-sm"></div><span className="text-xs text-slate-400 uppercase">Confidence</span></div>
                     <div className="flex items-center gap-2"><div className="w-3 h-3 bg-red-500 rounded-sm"></div><span className="text-xs text-slate-400 uppercase">Alert</span></div>
                </div>
              </div>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorAlert" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#475569" fontSize={10} axisLine={false} tickLine={false} />
                  <YAxis stroke="#475569" fontSize={10} axisLine={false} tickLine={false} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Area type="monotone" dataKey="confidence" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorConf)" />
                  <Area type="monotone" dataKey="is_alert" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorAlert)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Side Logs */}
            <div className="col-span-4 glass flex flex-col">
              <div className="p-6 border-b border-white/5">
                <h3 className="font-bold flex items-center gap-2">
                  <Clock size={16} className="text-blue-400" />
                  Recent Events
                </h3>
              </div>
              <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 custom-scrollbar">
                {logs.length === 0 ? (
                    <div className="h-full flex items-center justify-center text-slate-500 text-sm italic">
                        No activity recorded
                    </div>
                ) : logs.slice(0, 8).map((log, i) => (
                  <div key={i} className={`p-4 rounded-xl border ${log.is_alert ? 'bg-red-500/10 border-red-500/20' : 'bg-white/5 border-white/5'} transition-all`}>
                    <div className="flex justify-between items-start mb-1">
                      <span className={`text-[10px] font-bold uppercase tracking-widest ${log.is_alert ? 'text-red-400' : 'text-emerald-400'}`}>
                        {log.prediction}
                      </span>
                      <span className="text-[10px] text-slate-500">{log.timestamp}</span>
                    </div>
                    <p className="text-xs font-semibold mb-1">{log.packet_type}</p>
                    <div className="flex items-center gap-2">
                        <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                            <div className={`h-full ${log.is_alert ? 'bg-red-500' : 'bg-blue-500'}`} style={{width: `${log.confidence * 100}%`}}></div>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono">{(log.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'training' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Model Stats Cards */}
            <div className="col-span-4 glass p-6 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-400">SUPERVISED</span>
                  <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">● Active</span>
                </div>
                <h3 className="text-xl font-bold mb-2">Random Forest Classifier</h3>
                <p className="text-xs text-slate-400 mb-4">Classifies connection data into normal activity or intrusion attacks using a binary forest classifier.</p>
                <div className="flex flex-col gap-2 text-xs font-mono bg-white/5 p-3 rounded-lg border border-white/5">
                  <div className="flex justify-between"><span className="text-slate-500">Estimators:</span> <span>50</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Max Depth:</span> <span>20</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Precision (Intrusion):</span> <span className="text-emerald-400 font-bold">97%</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Recall (Intrusion):</span> <span className="text-emerald-400 font-bold">63%</span></div>
                </div>
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-4">File: models/rf_model.pkl</div>
            </div>

            <div className="col-span-4 glass p-6 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-400">UNSUPERVISED</span>
                  <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">● Active</span>
                </div>
                <h3 className="text-xl font-bold mb-2">Isolation Forest</h3>
                <p className="text-xs text-slate-400 mb-4">Detects outlier events and novel zero-day threats by partitioning points via isolation trees.</p>
                <div className="flex flex-col gap-2 text-xs font-mono bg-white/5 p-3 rounded-lg border border-white/5">
                  <div className="flex justify-between"><span className="text-slate-500">Contamination Rate:</span> <span>10%</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Bootstrap Samples:</span> <span>Auto</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Inliers Fitted:</span> <span>113,375</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Outliers Flagged:</span> <span>12,598</span></div>
                </div>
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-4">File: models/anomaly_detector.pkl</div>
            </div>

            <div className="col-span-4 glass p-6 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-400">DATA ENGINE</span>
                  <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">● Active</span>
                </div>
                <h3 className="text-xl font-bold mb-2">Preprocessing Pipeline</h3>
                <p className="text-xs text-slate-400 mb-4">Ingests raw connections, engineers domain-specific features, imputes, and scales values.</p>
                <div className="flex flex-col gap-2 text-xs font-mono bg-white/5 p-3 rounded-lg border border-white/5">
                  <div className="flex justify-between"><span className="text-slate-500">Scaler Used:</span> <span>RobustScaler</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Categorical OHE:</span> <span>Yes</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Custom Engineering:</span> <span>Packet rate, bytes ratio</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Feature Selection:</span> <span>RF SelectFromModel</span></div>
                </div>
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-4">File: models/preprocessing_engine.joblib</div>
            </div>

            {/* Training Logs / Pipeline Sequence */}
            <div className="col-span-12 glass p-6 mt-2">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Settings size={18} className="text-blue-400" />
                AI Training Pipeline Workflow
              </h3>
              <div className="grid grid-cols-5 gap-4">
                <div className="p-4 bg-white/5 rounded-xl border border-white/5 relative">
                  <div className="text-xs font-bold text-slate-400 mb-1">STEP 1</div>
                  <h4 className="text-sm font-bold text-white mb-2">Ingestion</h4>
                  <p className="text-[11px] text-slate-500">Loads training connection files (`KDDTrain+.txt`) using standard NSL-KDD column profiles.</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl border border-white/5 relative">
                  <div className="text-xs font-bold text-slate-400 mb-1">STEP 2</div>
                  <h4 className="text-sm font-bold text-white mb-2">Feature Engineering</h4>
                  <p className="text-[11px] text-slate-500">Calculates packet transmission rates, maps categorical attributes, scaling with robust rules.</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl border border-white/5 relative">
                  <div className="text-xs font-bold text-slate-400 mb-1">STEP 3</div>
                  <h4 className="text-sm font-bold text-white mb-2">Random Forest</h4>
                  <p className="text-[11px] text-slate-500">Fits 50 decision trees to binary classes (Normal vs Attack) using balanced class weights.</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl border border-white/5 relative">
                  <div className="text-xs font-bold text-slate-400 mb-1">STEP 4</div>
                  <h4 className="text-sm font-bold text-white mb-2">Isolation Forest</h4>
                  <p className="text-[11px] text-slate-500">Fits unsupervised isolation trees targeting the top 10% contamination anomalies.</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl border border-white/5 relative bg-blue-600/10 border-blue-600/20">
                  <div className="text-xs font-bold text-blue-400 mb-1">STEP 5</div>
                  <h4 className="text-sm font-bold text-white mb-2">Model Ingress</h4>
                  <p className="text-[11px] text-slate-400">Evaluation outputs are recorded and saved models are dynamically re-loaded by FastAPI.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {(activeTab === 'live' || activeTab === 'alerts') && (
            <div className="glass overflow-hidden flex flex-col h-[70vh]">
                <div className="p-6 border-b border-white/5 flex justify-between items-center">
                    <h3 className="text-xl font-bold font-['Outfit']">Real-time Data Stream</h3>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-ping"></div>
                        <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">Live Flow</span>
                    </div>
                </div>
                <div className="flex-1 overflow-y-auto p-0">
                    <table className="w-100 min-w-full text-left border-collapse">
                        <thead className="bg-white/5 text-[11px] font-bold uppercase text-slate-400 tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Timestamp</th>
                                <th className="px-6 py-4">Traffic Type</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">AI Score</th>
                                <th className="px-6 py-4">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {logs.map((log, i) => (
                                <tr key={i} className={`text-sm hover:bg-white/5 transition-colors ${log.is_alert ? 'bg-red-500/5' : ''}`}>
                                    <td className="px-6 py-4 font-mono text-slate-400">{log.timestamp}</td>
                                    <td className="px-6 py-4 font-bold">{log.packet_type}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${log.is_alert ? 'bg-red-500 text-white' : 'bg-emerald-500/20 text-emerald-500'}`}>
                                            {log.prediction}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-mono">{(log.confidence * 100).toFixed(2)}%</td>
                                    <td className="px-6 py-4">
                                        {log.is_alert ? (
                                            <button className="text-xs font-bold text-red-500 hover:underline">Quarantine</button>
                                        ) : (
                                            <span className="text-xs text-slate-500">None</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        )}
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${
        active 
        ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20 shadow-lg shadow-blue-600/5' 
        : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
      }`}
    >
      {React.cloneElement(icon, { size: 20 })}
      <span>{label}</span>
      {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-400 shadow-[0_0_8px_#3b82f6]"></div>}
    </button>
  );
}

function StatCard({ icon, label, value, subLabel, className = "", urgent = false }) {
  return (
    <div className={`glass p-6 group transition-all hover:scale-[1.02] ${className} ${urgent ? 'border-orange-500/30' : ''}`}>
      <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 border border-white/5 group-hover:border-white/10 group-hover:bg-white/10 transition-all">
        {icon}
      </div>
      <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">{label}</p>
      <h4 className="text-3xl font-bold text-white mb-2">{value}</h4>
      <p className="text-slate-500 text-xs font-medium flex items-center gap-1">
        {urgent ? <AlertTriangle size={12} className="text-orange-500" /> : <CheckCircle2 size={12} className="text-emerald-500" />}
        {subLabel}
      </p>
    </div>
  );
}

export default App;
