import React from 'react';
import { Activity, Shield, Sparkles, UserCheck, Lock } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, user, onSignOut }) {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      borderBottom: '1px solid var(--line)',
      background: 'rgba(8, 8, 10, 0.75)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
    }}>
      <div style={{
        maxWidth: '1320px',
        margin: '0 auto',
        padding: '0 28px',
        height: '64px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Brand Logo & Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          <button 
            onClick={() => setActiveTab('landing')} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px' }}
          >
            <div style={{
              width: '34px',
              height: '34px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(167, 60, 255, 0.4)',
            }}>
              <Activity size={20} color="#ffffff" />
            </div>
            <div style={{ textAlign: 'left' }}>
              <span style={{ fontSize: '17px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text)' }}>
                CARE-XAI
              </span>
              <span style={{ display: 'block', fontSize: '10px', color: 'var(--text-3)', fontWeight: 500, letterSpacing: '0.05em' }}>
                CMMD1 MULTIMODAL MVP
              </span>
            </div>
          </button>

          {/* Navigation Links */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button 
              className={`sd-btn ${activeTab === 'landing' ? 'sd-btn-accent' : 'sd-btn-ghost'}`}
              onClick={() => setActiveTab('landing')}
              style={{ fontSize: '13.5px', height: '36px' }}
            >
              <Sparkles size={14} /> Overview
            </button>
            <button 
              className={`sd-btn ${activeTab === 'dashboard' ? 'sd-btn-accent' : 'sd-btn-ghost'}`}
              onClick={() => setActiveTab('dashboard')}
              style={{ fontSize: '13.5px', height: '36px' }}
            >
              <Activity size={14} /> Diagnostic Workstation
            </button>
          </nav>
        </div>

        {/* Right Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span className="sd-pill sd-pill-success" style={{ fontSize: '11.5px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)', display: 'inline-block' }}></span>
            FastAPI PyTorch Live
          </span>

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 12px 4px 6px',
                borderRadius: '999px',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid var(--line)',
              }}>
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--accent), var(--accent-blue))',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '12px',
                }}>
                  {user.name.charAt(0)}
                </div>
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-2)' }}>{user.name}</span>
              </div>
              <button className="sd-btn sd-btn-ghost" onClick={onSignOut} style={{ fontSize: '12.5px', padding: '6px 12px' }}>
                Sign Out
              </button>
            </div>
          ) : (
            <button 
              className="sd-btn sd-btn-accent sd-pulse-glow" 
              onClick={() => setActiveTab('login')}
              style={{ fontSize: '13.5px', height: '38px', padding: '0 20px' }}
            >
              <Lock size={14} /> Clinical Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
