import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { BookOpen, Award, Target, Zap, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState({
    activePlan: 'None',
    certifications: 0,
    assessments: 0
  });

  useEffect(() => {
    const fetchRecentActivity = async () => {
      try {
        const response = await api.get('/learn/jobs');
        const allJobs = response.data;
        setJobs(allJobs.slice(0, 3)); // Top 3 recent jobs
        
        const plans = allJobs.filter(j => j.rawPrompt?.includes('[LEARNING_PLAN]'));
        const assessments = allJobs.filter(j => j.rawPrompt?.includes('[ASSESSMENT]'));
        
        let activePlanName = 'None';
        if (plans.length > 0) {
          const match = plans[0].rawPrompt.match(/goal=([^,]+)/);
          activePlanName = match ? match[1] : 'Custom Plan';
        }

        setStats({
          activePlan: activePlanName,
          certifications: assessments.filter(j => j.status === 'completed').length,
          assessments: assessments.length
        });
      } catch (err) {
        console.error("Failed to fetch jobs", err);
      }
    };
    fetchRecentActivity();
  }, []);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>Welcome back, {user?.fullName || user?.email}</h1>
        <p style={{ color: 'var(--text-muted)' }}>Here is your Enterprise Learning overview.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px' }}>
              <Target size={24} color="var(--primary-color)" />
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Active Plan</div>
              <div style={{ fontWeight: 'bold' }}>{stats.activePlan}</div>
            </div>
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: stats.activePlan !== 'None' ? '45%' : '0%' }}></div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span>Progress</span>
            <span>{stats.activePlan !== 'None' ? '45%' : '0%'}</span>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
              <Award size={24} color="var(--success)" />
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Certifications</div>
              <div style={{ fontWeight: 'bold' }}>{stats.certifications} Completed</div>
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px' }}>
              <Zap size={24} color="var(--warning)" />
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Next Study Block</div>
              <div style={{ fontWeight: 'bold' }}>{stats.activePlan !== 'None' ? 'Today, 4 PM' : 'No Active Plan'}</div>
            </div>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>via Work IQ Calendar Sync</div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>
              <BookOpen size={24} color="var(--danger)" />
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Assessments</div>
              <div style={{ fontWeight: 'bold' }}>{stats.assessments} Total Taken</div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={18} /> Recent AI Generations
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {jobs.length === 0 ? (
              <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                No recent activity. Try generating a study plan!
              </div>
            ) : (
              jobs.map(job => (
                <div key={job.jobId} className="glass-card" style={{ padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: '500', marginBottom: '0.25rem' }}>
                      {job.rawPrompt?.includes('[LEARNING_PLAN]') ? 'Study Plan Generation' : 'Assessment Generation'}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                      {job.rawPrompt.replace('[LEARNING_PLAN] ', '').replace('[ASSESSMENT] ', '')}
                    </div>
                  </div>
                  <div>
                    <span className={`badge ${job.status === 'completed' ? 'badge-success' : job.status === 'failed' ? 'badge-danger' : 'badge-warning'}`}>
                      {job.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        <div>
          <h3 style={{ marginBottom: '1rem' }}>Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <Link to="/plan" className="glass-card" style={{ padding: '1.25rem', display: 'block', textDecoration: 'none', color: 'var(--text-main)' }}>
              <div style={{ fontWeight: '500', marginBottom: '0.25rem', color: 'var(--primary-color)' }}>Generate Study Plan &rarr;</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Get a capacity-aware path</div>
            </Link>
            <Link to="/assess" className="glass-card" style={{ padding: '1.25rem', display: 'block', textDecoration: 'none', color: 'var(--text-main)' }}>
              <div style={{ fontWeight: '500', marginBottom: '0.25rem', color: 'var(--primary-color)' }}>Take Assessment &rarr;</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Scenario-based questions</div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
