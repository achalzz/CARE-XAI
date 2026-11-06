import React, { useState } from 'react';
import { X, Lock, Mail, ShieldCheck, UserCheck, ArrowRight, Sparkles } from 'lucide-react';

export default function SignInModal({ isOpen, onClose, onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Radiologist Specialist');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      onLoginSuccess({
        email: email || 'dr.smith@care-xai.med',
        name: email ? email.split('@')[0] : 'Dr. Sarah Smith',
        role: role,
      });
      setLoading(false);
      onClose();
    }, 600);
  };

  const handleDemoLogin = () => {
    setEmail('dr.sarah.smith@radiology.org');
    setPassword('demo123456');
    setLoading(true);
    setTimeout(() => {
      onLoginSuccess({
        email: 'dr.sarah.smith@radiology.org',
        name: 'Dr. Sarah Smith, MD',
        role: 'Chief Mammographer & XAI Lead',
      });
      setLoading(false);
      onClose();
    }, 500);
  };

  return (
    <div className="sd-modal-backdrop" onClick={onClose}>
      <div 
        className="sd-glass-card-glow" 
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '460px',
          padding: '36px',
          position: 'relative',
          background: 'rgba(12, 12, 18, 0.85)',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(167, 60, 255, 0.25)',
          border: '1px solid rgba(167, 60, 255, 0.3)',
        }}
      >
        {/* Close Button */}
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'none',
            border: 'none',
            color: 'var(--text-3)',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '50%',
            transition: 'color 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = 'var(--text)'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-3)'}
        >
          <X size={20} />
        </button>

        {/* Header Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
            boxShadow: '0 0 24px rgba(167, 60, 255, 0.4)',
          }}>
            <Lock size={24} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text)' }}>
            Clinical Portal Access
          </h2>
          <p style={{ fontSize: '13.5px', color: 'var(--text-2)', marginTop: '6px' }}>
            Authenticate to access CARE-XAI diagnostic workstation
          </p>
        </div>

        {/* Quick Demo Clinician Banner */}
        <div style={{
          padding: '12px 16px',
          borderRadius: '12px',
          background: 'rgba(15, 204, 206, 0.08)',
          border: '1px solid rgba(15, 204, 206, 0.25)',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={16} color="var(--accent-2)" />
            <span style={{ fontSize: '12.5px', color: 'var(--text)', fontWeight: 500 }}>
              Testing interface?
            </span>
          </div>
          <button 
            type="button"
            className="sd-btn sd-btn-cyan"
            onClick={handleDemoLogin}
            style={{ fontSize: '12px', padding: '6px 14px', height: '32px' }}
          >
            Quick Demo Login
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-2)', marginBottom: '6px' }}>
              Work Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="var(--text-3)" style={{ position: 'absolute', left: '14px', top: '14px' }} />
              <input 
                type="email" 
                required 
                placeholder="clinician@hospital.org"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="sd-input"
                style={{ paddingLeft: '40px' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-2)', marginBottom: '6px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="var(--text-3)" style={{ position: 'absolute', left: '14px', top: '14px' }} />
              <input 
                type="password" 
                required 
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="sd-input"
                style={{ paddingLeft: '40px' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-2)', marginBottom: '6px' }}>
              Clinical Role
            </label>
            <select 
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="sd-input"
              style={{ cursor: 'pointer', background: '#0e0e14' }}
            >
              <option value="Radiologist Specialist">Radiologist Specialist</option>
              <option value="Oncology Consultant">Oncology Consultant</option>
              <option value="AI Research Clinician">AI Research Clinician</option>
            </select>
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="sd-btn sd-btn-accent sd-pulse-glow"
            style={{ width: '100%', height: '46px', marginTop: '8px', fontSize: '15px' }}
          >
            {loading ? 'Authenticating...' : (
              <>Sign In to Workstation <ArrowRight size={16} /></>
            )}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '11.5px', color: 'var(--text-3)' }}>
          <ShieldCheck size={14} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '4px' }} />
          HIPAA & GDPR Compliant Encrypted Session
        </div>
      </div>
    </div>
  );
}
