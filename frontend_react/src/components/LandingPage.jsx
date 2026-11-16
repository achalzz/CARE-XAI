import React from 'react';
import { 
  Activity, 
  ArrowRight, 
  ShieldCheck, 
  Sparkles, 
  Layers, 
  Cpu, 
  Eye, 
  BarChart3, 
  CheckCircle2,
  FileCode,
  Zap,
  Terminal
} from 'lucide-react';

export default function LandingPage({ onLaunchWorkstation, onOpenSignIn, onExploreArchitecture }) {
  return (
    <div style={{ position: 'relative', overflow: 'hidden', minHeight: '90vh' }}>
      
      {/* Background Glow Orbs */}
      <div style={{
        position: 'absolute',
        top: '-150px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '800px',
        height: '450px',
        background: 'radial-gradient(ellipse at center, rgba(167, 60, 255, 0.2) 0%, rgba(15, 204, 206, 0.08) 50%, rgba(8, 8, 10, 0) 80%)',
        pointerEvents: 'none',
        zIndex: 0,
      }}></div>

      {/* Hero Section */}
      <section style={{ position: 'relative', zIndex: 1, maxWidth: '1280px', margin: '0 auto', padding: '64px 28px 48px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '56px', alignItems: 'center' }}>
          
          {/* Left Column Text */}
          <div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center', marginBottom: '20px' }}>
              <span className="sd-pill sd-pill-accent">
                <Sparkles size={13} /> CARE-XAI Framework v1.0
              </span>
              <span className="sd-pill sd-pill-cyan">
                <ShieldCheck size={13} /> CMMD Dual-View Dataset Tested
              </span>
            </div>

            <h1 style={{
              fontSize: 'clamp(40px, 5.2vw, 68px)',
              fontWeight: 700,
              letterSpacing: '-0.04em',
              lineHeight: 1.04,
              margin: '0 0 24px',
            }}>
              Confidence-Aware Robust Explainable <br />
              <span className="sd-gradient-text">Multimodal AI.</span>
            </h1>

            <p style={{
              fontSize: '17px',
              color: 'var(--text-2)',
              lineHeight: 1.6,
              maxWidth: '540px',
              margin: '0 0 32px',
            }}>
              Integrating dual-view mammography with clinical risk factors using gated cross-attention fusion, 
              <span style={{ color: 'var(--text)', fontWeight: 600 }}> MC dropout epistemic uncertainty</span>, and 
              <span className="sd-serif" style={{ color: 'var(--accent-2)', fontSize: '1.08em' }}> Grad-CAM++ interpretability.</span>
            </p>

            <div style={{ display: 'flex', gap: '14px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '32px' }}>
              <button 
                className="sd-btn sd-btn-accent sd-pulse-glow" 
                onClick={onLaunchWorkstation}
                style={{ height: '52px', padding: '0 26px', fontSize: '15px' }}
              >
                Launch Diagnostic Workstation <ArrowRight size={17} />
              </button>
              <button 
                className="sd-btn sd-btn-cyan" 
                onClick={onExploreArchitecture}
                style={{ height: '52px', padding: '0 22px', fontSize: '15px' }}
              >
                <Cpu size={16} /> How It Works (Pipeline)
              </button>
              <button 
                className="sd-btn" 
                onClick={onOpenSignIn}
                style={{ height: '52px', padding: '0 20px', fontSize: '14.5px' }}
              >
                Clinical Sign In
              </button>
            </div>

            {/* Quick Metrics */}
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', pt: '8px' }}>
              <div>
                <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text)' }}>94.2%</div>
                <div style={{ fontSize: '12px', color: 'var(--text-3)' }}>Multimodal AUC-ROC</div>
              </div>
              <div style={{ borderLeft: '1px solid var(--line)', paddingLeft: '24px' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--accent-2)' }}>15× MC</div>
                <div style={{ fontSize: '12px', color: 'var(--text-3)' }}>Uncertainty Passes</div>
              </div>
              <div style={{ borderLeft: '1px solid var(--line)', paddingLeft: '24px' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--accent)' }}>Grad-CAM++</div>
                <div style={{ fontSize: '12px', color: 'var(--text-3)' }}>Saliency Attention</div>
              </div>
            </div>

          </div>

          {/* Right Column: Sixth-style Terminal Card Preview */}
          <div className="sd-glass-card-glow" style={{ padding: '20px', borderRadius: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '12px', marginBottom: '16px', borderBottom: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Terminal size={15} color="var(--accent-2)" />
                <span className="sd-mono" style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-2)' }}>CARE-XAI DIAGNOSTIC ENGINE</span>
              </div>
              <span className="sd-pill sd-pill-success" style={{ fontSize: '10.5px' }}>PyTorch 2.2 CUDA</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '12.5px' }}>
              
              {/* Simulated Step 1 */}
              <div style={{ borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', border: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text)' }}>Patient ID: D1-0006 (Age 46)</span>
                  <span className="sd-mono" style={{ color: 'var(--accent-2)', fontSize: '11px' }}>DICOM Ready</span>
                </div>
                <span className="sd-mono" style={{ color: 'var(--text-3)', fontSize: '11px' }}>Loaded CC & MLO mammogram views (384×384)</span>
              </div>

              {/* Simulated Step 2 */}
              <div style={{ borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', border: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text)' }}>Gated Cross-Attention Fusion</span>
                  <span className="sd-mono" style={{ color: 'var(--accent)', fontSize: '11px' }}>W_img: 0.72 | W_clin: 0.28</span>
                </div>
                <div style={{ height: '5px', borderRadius: '4px', background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: '72%', background: 'linear-gradient(90deg, var(--accent), var(--accent-2))' }}></div>
                </div>
              </div>

              {/* Simulated Step 3 */}
              <div style={{ borderRadius: '10px', background: 'rgba(167, 60, 255, 0.08)', padding: '12px 14px', border: '1px solid rgba(167, 60, 255, 0.25)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 700, color: '#ffffff' }}>Diagnostic Output</span>
                  <span className="sd-pill sd-pill-danger" style={{ fontSize: '11px', fontWeight: 700 }}>MALIGNANT (88.4%)</span>
                </div>
                <div style={{ display: 'flex', gap: '12px', fontSize: '11.5px', color: 'var(--text-2)' }}>
                  <div>Std: <span style={{ color: 'var(--success)', fontWeight: 600 }}>0.042 (Low)</span></div>
                  <div>Entropy: <span style={{ color: 'var(--success)', fontWeight: 600 }}>0.361</span></div>
                  <div>Safety: <span style={{ color: 'var(--success)', fontWeight: 600 }}>SAFE_TO_TRUST</span></div>
                </div>
              </div>

              {/* Action Button inside preview */}
              <button 
                className="sd-btn sd-btn-cyan"
                onClick={onLaunchWorkstation}
                style={{ width: '100%', height: '40px', marginTop: '6px', fontSize: '13px' }}
              >
                Inspect Patient D1-0006 Workstation <ArrowRight size={14} />
              </button>

            </div>
          </div>

        </div>
      </section>

      {/* Marquee Banner */}
      <section style={{ borderTop: '1px solid var(--line)', borderBottom: '1px solid var(--line)', padding: '20px 0', background: 'rgba(255, 255, 255, 0.01)' }}>
        <div style={{ textAlign: 'center', fontSize: '11px', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.16em', marginBottom: '14px' }}>
          Multimodal Explainable AI Diagnostics · Key Features
        </div>
        <div className="sd-marquee">
          <div className="sd-marquee-track">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
              <Layers size={16} color="var(--accent)" /> Dual-View Mammography (CC + MLO)
            </span>
            <span style={{ color: 'var(--line-accent)' }}>◆</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={16} color="var(--accent-2)" /> MC Dropout Uncertainty Quantified
            </span>
            <span style={{ color: 'var(--line-accent)' }}>◆</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
              <Eye size={16} color="var(--success)" /> Grad-CAM++ Saliency Heatmaps
            </span>
            <span style={{ color: 'var(--line-accent)' }}>◆</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
              <BarChart3 size={16} color="var(--warning)" /> Counterfactual Modality Ablation
            </span>
            <span style={{ color: 'var(--line-accent)' }}>◆</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
              <ShieldCheck size={16} color="var(--accent)" /> High-Uncertainty Safety Flags
            </span>
            <span style={{ color: 'var(--line-accent)' }}>◆</span>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section style={{ maxWidth: '1280px', margin: '0 auto', padding: '72px 28px' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{ fontSize: '11px', color: 'var(--accent-2)', textTransform: 'uppercase', letterSpacing: '0.14em', marginBottom: '8px' }}>
            System Architecture
          </div>
          <h2 style={{ fontSize: '36px', fontWeight: 700, letterSpacing: '-0.03em', color: 'var(--text)' }}>
            Why Clinicians Trust <span className="sd-gradient-text">CARE-XAI</span>
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
          
          {/* Card 1 */}
          <div className="sd-glass-card" style={{ padding: '28px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'rgba(167, 60, 255, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <Layers size={22} color="var(--accent)" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text)', marginBottom: '10px' }}>
              Multimodal Gated Fusion
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55 }}>
              Combines deep features from ResNet DICOM image backbones with standardized clinical age metrics via dynamic attention weight gates.
            </p>
          </div>

          {/* Card 2 */}
          <div className="sd-glass-card" style={{ padding: '28px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'rgba(15, 204, 206, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <Cpu size={22} color="var(--accent-2)" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text)', marginBottom: '10px' }}>
              MC Dropout Uncertainty
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55 }}>
              Executes Monte Carlo stochastic forward passes to compute predictive standard deviation and entropy, flagging ambiguous cases.
            </p>
          </div>

          {/* Card 3 */}
          <div className="sd-glass-card" style={{ padding: '28px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'rgba(111, 224, 168, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <BarChart3 size={22} color="var(--success)" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text)', marginBottom: '10px' }}>
              Modality Counterfactuals
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55 }}>
              Simulates zero-masking image vs clinical inputs independently to isolate exactly how much each modality drives the diagnostic prediction.
            </p>
          </div>

          {/* Card 4 */}
          <div className="sd-glass-card" style={{ padding: '28px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'rgba(255, 183, 3, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <Eye size={22} color="var(--warning)" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text)', marginBottom: '10px' }}>
              Grad-CAM++ Interpretability
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55 }}>
              Generates pixel-accurate visual attention heatmaps localized to suspicious breast tissue lesions for radiologist audit.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
}
