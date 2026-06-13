import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Users, AlertTriangle, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

const ManagerDashboard = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await api.get('/manager/insights');
        setInsights(response.data);
      } catch (err) {
        if (err.response?.status === 403) {
          setError('Access Denied. You must have MANAGER role to view this page.');
        } else {
          setError('Failed to fetch manager insights. Ensure the AI Engine and Gateway are running.');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <Loader2 size={48} color="var(--primary-color)" style={{ animation: 'spin 2s linear infinite', marginBottom: '1rem' }} />
        <h3>Manager Insights Agent is analyzing your team...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ color: 'var(--danger)', padding: '1.5rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}><AlertTriangle /> Error</h3>
          <p style={{ marginTop: '0.5rem' }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <Users size={28} color="var(--primary-color)" />
          <h1 style={{ margin: 0 }}>Team Insights</h1>
        </div>
        <p style={{ color: 'var(--text-muted)' }}>AI-generated analytics across your organization.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Total Teams</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{insights?.metrics?.total_teams || 3}</div>
        </div>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Avg Completion</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>
            {insights?.metrics?.average_completion_rate || '68%'}
          </div>
        </div>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
            Top Skill
            <TrendingUp size={16} color="var(--success)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{insights?.metrics?.top_skill || 'Azure DevOps'}</div>
        </div>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
            Risk Area
            <TrendingDown size={16} color="var(--danger)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{insights?.metrics?.highest_risk_area || 'Kubernetes'}</div>
        </div>
      </div>

      <div className="glass-card markdown-body" style={{ padding: '2.5rem' }}>
        <ReactMarkdown>{insights?.report}</ReactMarkdown>
      </div>

    </motion.div>
  );
};

export default ManagerDashboard;
