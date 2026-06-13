import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';
import { Trash2 } from 'lucide-react';

const JobHistory = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await api.get('/learn/jobs');
        setJobs(response.data);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch jobs", err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);
  const handleDelete = async (jobId) => {
    try {
      await api.delete(`/learn/jobs/${jobId}`);
      setJobs(jobs.filter(j => j.jobId !== jobId));
    } catch (err) {
      console.error("Failed to delete job", err);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '0.5rem' }}>Job History</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>View your past learning generations</p>

      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '500' }}>Query</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '500' }}>Status</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '500' }}>Date</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '500' }}>Confidence</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '500', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading history...</td>
              </tr>
            ) : jobs.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No learning jobs found.</td>
              </tr>
            ) : (
              jobs.map(job => (
                <tr key={job.jobId} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem' }}>{job.rawPrompt}</td>
                  <td style={{ padding: '1rem' }}>
                    <span style={{ 
                      color: job.status === 'completed' ? 'var(--success)' : job.status === 'failed' ? 'var(--danger)' : 'var(--warning)', 
                      padding: '0.25rem 0.5rem', 
                      backgroundColor: job.status === 'completed' ? 'rgba(16, 185, 129, 0.1)' : job.status === 'failed' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)', 
                      borderRadius: '4px', fontSize: '0.875rem' 
                    }}>
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{new Date(job.createdAt).toLocaleDateString()}</td>
                  <td style={{ padding: '1rem', fontWeight: 'bold' }}>{job.confidenceScore ? `${job.confidenceScore}%` : '-'}</td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
                    <button onClick={() => handleDelete(job.jobId)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', opacity: 0.7 }} onMouseOver={e => e.currentTarget.style.opacity = 1} onMouseOut={e => e.currentTarget.style.opacity = 0.7}>
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default JobHistory;
