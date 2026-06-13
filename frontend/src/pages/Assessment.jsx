import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Send, Loader2, GraduationCap, Target } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

const Assessment = () => {
  const { user } = useAuth();
  const [cert, setCert] = useState('AZ-204');
  
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, polling, completed, failed
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  const submitAssessment = async (e) => {
    e.preventDefault();
    if (!cert.trim()) return;

    setStatus('polling');
    setError('');
    setReport(null);

    try {
      const response = await api.post('/learn/assess', { 
        targetCertification: cert
      });
      setJobId(response.data.jobId);
    } catch (err) {
      setError('Failed to submit assessment request. Ensure backend is running.');
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
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ maxWidth: '700px', margin: '0 auto', marginTop: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <GraduationCap size={28} color="var(--primary-color)" />
            <h1 style={{ margin: 0 }}>Certification Assessment</h1>
          </div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
            The Assessment Agent will generate practice questions grounded in Foundry IQ's real enterprise scenarios.
          </p>

          {error && <div style={{ color: 'var(--danger)', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>{error}</div>}

          <form onSubmit={submitAssessment} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Target size={16}/> Target Certification
              </label>
              <input
                type="text"
                className="input-field"
                value={cert}
                onChange={(e) => setCert(e.target.value)}
                placeholder="e.g. AZ-204"
                required
              />
            </div>

            <div style={{ padding: '1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              <strong>Note:</strong> Assessment questions are tailored for employee <strong>{user?.employeeId}</strong> based on past internal project history in Fabric IQ.
            </div>

            <button type="submit" className="btn-primary" disabled={!cert.trim()} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <Send size={18} />
              Generate Practical Assessment
            </button>
          </form>
        </motion.div>
      );
    }

    if (status === 'polling') {
      return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card" style={{ maxWidth: '600px', margin: '0 auto', marginTop: '4rem', textAlign: 'center', padding: '4rem 2rem' }}>
          <Loader2 size={48} color="var(--primary-color)" style={{ animation: 'spin 2s linear infinite', margin: '0 auto 2rem' }} />
          <h2>Assessment Agent Generating Questions...</h2>
          <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Retrieving architectural patterns from Foundry IQ for scenario-based questions.</p>
        </motion.div>
      );
    }

    if (status === 'completed' && report) {
      return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <GraduationCap size={24} color="var(--primary-color)" />
                <h1 style={{ margin: 0 }}>Practical Assessment</h1>
              </div>
              <p style={{ color: 'var(--text-muted)' }}>Target: {cert}</p>
            </div>
            <button onClick={() => { setStatus('idle'); setCert(''); }} className="btn-secondary">New Assessment</button>
          </div>

          <div className="glass-card markdown-body" style={{ padding: '2rem' }}>
            <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
               <h2 style={{ marginTop: 0 }}>Foundry IQ Grounded Scenarios</h2>
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

export default Assessment;
