import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Send, Loader2, FileText, LayoutList, GitCommit, CheckCircle2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

const NewResearch = () => {
  const [query, setQuery] = useState('');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, polling, completed, failed
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summary'); // summary, detail, citations

  const submitQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setStatus('polling');
    setError('');
    setReport(null);

    try {
      const response = await api.post('/research/query', { query });
      setJobId(response.data.jobId);
    } catch (err) {
      if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please wait a minute before trying again.');
      } else {
        setError('Failed to submit query. Ensure backend is running.');
      }
      setStatus('idle');
    }
  };

  useEffect(() => {
    let intervalId;

    const pollStatus = async () => {
      try {
        const res = await api.get(`/research/jobs/${jobId}`);
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
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ maxWidth: '800px', margin: '0 auto', marginTop: '4rem' }}>
          <h1 style={{ marginBottom: '1rem' }}>New Research Task</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
            Enter a topic, question, or industry to generate an autonomous deep-dive report.
          </p>

          {error && <div style={{ color: 'var(--danger)', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>{error}</div>}

          <form onSubmit={submitQuery}>
            <textarea
              className="input-field"
              rows={5}
              placeholder="E.g., How do Graph Neural Networks improve fraud detection in financial systems?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ resize: 'vertical', marginBottom: '1rem', fontSize: '1.1rem' }}
            />
            <button type="submit" className="btn-primary" disabled={!query.trim()} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: 'auto' }}>
              <Send size={18} />
              Launch Agent
            </button>
          </form>
        </motion.div>
      );
    }

    if (status === 'polling') {
      return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card" style={{ maxWidth: '600px', margin: '0 auto', marginTop: '4rem', textAlign: 'center', padding: '4rem 2rem' }}>
          <Loader2 size={48} color="var(--primary-color)" style={{ animation: 'spin 2s linear infinite', margin: '0 auto 2rem' }} />
          <h2>AI Agent is Synthesizing...</h2>
          <div style={{ marginTop: '2rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Job ID: {jobId}</div>
        </motion.div>
      );
    }

    if (status === 'completed' && report) {
      return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
            <div>
              <h1 style={{ marginBottom: '0.5rem' }}>Research Complete</h1>
              <p style={{ color: 'var(--text-muted)' }}>"{report.rawPrompt}"</p>
            </div>
            <button onClick={() => { setStatus('idle'); setQuery(''); }} className="btn-secondary">New Query</button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
            <div className="glass-card" style={{ padding: '1rem 1.5rem' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Confidence Score</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>{report.confidenceScore}%</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem 1.5rem' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Iterations</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{report.iterationCount} / 3</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem 1.5rem' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Processing Time</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{(report.processingTimeMs / 1000).toFixed(1)}s</div>
            </div>
          </div>

          <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(0,0,0,0.2)' }}>
              <button 
                onClick={() => setActiveTab('summary')}
                style={{ flex: 1, padding: '1rem', background: 'transparent', border: 'none', color: activeTab === 'summary' ? 'var(--primary-color)' : 'var(--text-muted)', borderBottom: activeTab === 'summary' ? '2px solid var(--primary-color)' : '2px solid transparent', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
              >
                <LayoutList size={18} /> Executive Summary
              </button>
              <button 
                onClick={() => setActiveTab('detail')}
                style={{ flex: 1, padding: '1rem', background: 'transparent', border: 'none', color: activeTab === 'detail' ? 'var(--primary-color)' : 'var(--text-muted)', borderBottom: activeTab === 'detail' ? '2px solid var(--primary-color)' : '2px solid transparent', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
              >
                <FileText size={18} /> Deep Dive Analysis
              </button>
              <button 
                onClick={() => setActiveTab('citations')}
                style={{ flex: 1, padding: '1rem', background: 'transparent', border: 'none', color: activeTab === 'citations' ? 'var(--primary-color)' : 'var(--text-muted)', borderBottom: activeTab === 'citations' ? '2px solid var(--primary-color)' : '2px solid transparent', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
              >
                <GitCommit size={18} /> Citations
              </button>
            </div>
            
            <div style={{ padding: '2rem' }} className="markdown-body">
              {activeTab === 'summary' && <ReactMarkdown>{report.executiveSummary}</ReactMarkdown>}
              {activeTab === 'detail' && <ReactMarkdown>{report.detailedContent}</ReactMarkdown>}
              {activeTab === 'citations' && (
                <div>
                  <h3>Sources Consulted</h3>
                  <pre style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', overflowX: 'auto' }}>
                    {JSON.stringify(JSON.parse(report.citations || '[]'), null, 2)}
                  </pre>
                </div>
              )}
            </div>
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

export default NewResearch;
