import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Send, Loader2, BookOpen, Clock, Target, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

const StudyPlan = () => {
  const { user } = useAuth();
  const [role, setRole] = useState('Cloud Engineer');
  const [goal, setGoal] = useState('');
  const [experience, setExperience] = useState('intermediate');
  const [weeks, setWeeks] = useState(6);
  
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, polling, completed, failed
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  const submitPlan = async (e) => {
    e.preventDefault();
    if (!goal.trim()) return;

    setStatus('polling');
    setError('');
    setReport(null);

    try {
      const response = await api.post('/learn/plan', { 
        role, 
        goal, 
        experienceLevel: experience,
        weeksAvailable: weeks
      });
      setJobId(response.data.jobId);
    } catch (err) {
      setError('Failed to submit learning plan request. Ensure backend is running.');
      setStatus('idle');
    }
  };

  useEffect(() => {
    let intervalId;

    const pollStatus = async () => {
      try {
        const res = await api.get(`/learn/jobs/${jobId}`);
        const job = res.data;

        if (job.status === 'completed') {
          setReport(job);
          setStatus('completed');
          clearInterval(intervalId);
        } else if (job.status === 'failed') {
          setError(job.errorMessage || 'Job failed during AI synthesis.');
          setStatus('failed');
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error('Polling error', err);
      }
    };

    if (status === 'polling' && jobId) {
      pollStatus(); // initial check
      intervalId = setInterval(pollStatus, 3000); // poll every 3s
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [status, jobId]);

  const renderContent = () => {
    if (status === 'idle' || status === 'failed') {
      return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ maxWidth: '800px', margin: '0 auto', marginTop: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <BookOpen size={28} color="var(--primary-color)" />
            <h1 style={{ margin: 0 }}>Generate Study Plan</h1>
          </div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
            Get a personalized learning path and capacity-aware schedule powered by Foundry IQ, Work IQ, and Fabric IQ.
          </p>

          {error && <div style={{ color: 'var(--danger)', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>{error}</div>}

          <form onSubmit={submitPlan} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            <div style={{ display: 'flex', gap: '1.5rem' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><User size={16}/> Current Role</label>
                <input
                  type="text"
                  className="input-field"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  placeholder="e.g. Cloud Engineer"
                  required
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Target size={16}/> Learning Goal</label>
                <input
                  type="text"
                  className="input-field"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g. Get AZ-204 certified"
                  required
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1.5rem' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>Experience Level</label>
                <select 
                  className="input-field" 
                  value={experience} 
                  onChange={(e) => setExperience(e.target.value)}
                  style={{ appearance: 'none', backgroundColor: 'rgba(15, 23, 42, 0.6)' }}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Clock size={16}/> Target Timeline (Weeks)</label>
                <input
                  type="number"
                  className="input-field"
                  min="1" max="12"
                  value={weeks}
                  onChange={(e) => setWeeks(parseInt(e.target.value))}
                  required
                />
              </div>
            </div>

            <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              <strong>Work IQ Integration Active:</strong> The generated plan will automatically read your meeting load and calendar signals for employee <strong>{user?.employeeId}</strong> to find the best study windows.
            </div>

            <button type="submit" className="btn-primary" disabled={!goal.trim()} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
              <Send size={18} />
              Generate Learning Path & Schedule
            </button>
          </form>
        </motion.div>
      );
    }

    if (status === 'polling') {
      return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card" style={{ maxWidth: '600px', margin: '0 auto', marginTop: '4rem', textAlign: 'center', padding: '4rem 2rem' }}>
          <Loader2 size={48} color="var(--primary-color)" style={{ animation: 'spin 2s linear infinite', margin: '0 auto 2rem' }} />
          <h2>Curator & Study Plan Agents are working...</h2>
          <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Analyzing your Fabric IQ profile and Work IQ capacity constraints.</p>
        </motion.div>
      );
    }

    if (status === 'completed' && report) {
      return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <BookOpen size={24} color="var(--primary-color)" />
                <h1 style={{ margin: 0 }}>Your Custom Study Plan</h1>
              </div>
              <p style={{ color: 'var(--text-muted)' }}>Generated for {role} targeting "{goal}"</p>
            </div>
            <button onClick={() => { setStatus('idle'); setGoal(''); }} className="btn-secondary">New Plan</button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
             <div className="stat-box">
               <div className="stat-value" style={{ color: 'var(--success)' }}>Active</div>
               <div className="stat-label">Work IQ Capacity Routing</div>
             </div>
             <div className="stat-box">
               <div className="stat-value">{report.iterationCount}</div>
               <div className="stat-label">Agents Orchestrated</div>
             </div>
             <div className="stat-box">
               <div className="stat-value">{(report.processingTimeMs / 1000).toFixed(1)}s</div>
               <div className="stat-label">Processing Time</div>
             </div>
          </div>

          <div className="glass-card markdown-body" style={{ padding: '2rem' }}>
            <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <h2 style={{ marginTop: 0 }}>Executive Summary</h2>
              <ReactMarkdown>{report.executiveSummary}</ReactMarkdown>
            </div>
            <ReactMarkdown>{report.detailedContent}</ReactMarkdown>
          </div>
        </motion.div>
      );
    }
  };

  return (
    <div style={{ minHeight: '100%' }}>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
      <AnimatePresence mode="wait">
        {renderContent()}
      </AnimatePresence>
    </div>
  );
};

export default StudyPlan;
