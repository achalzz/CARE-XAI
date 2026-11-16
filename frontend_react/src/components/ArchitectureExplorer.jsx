import React, { useState } from 'react';
import { 
  Activity, 
  Layers, 
  Cpu, 
  Eye, 
  ShieldCheck, 
  GitMerge, 
  Sliders, 
  Info, 
  CheckCircle2, 
  ArrowRight,
  Database,
  HelpCircle,
  AlertTriangle,
  Sparkles
} from 'lucide-react';

export default function ArchitectureExplorer({ onLaunchWorkstation }) {
  // Interactive Simulation State
  const [imageClarity, setImageClarity] = useState(85); // 0 - 100
  const [patientAge, setPatientAge] = useState(48); // 20 - 90
  const [activeStep, setActiveStep] = useState(0);

  // Computed gating simulation based on inputs
  const simulatedImageWeight = Math.round(
    Math.min(92, Math.max(25, (imageClarity * 0.75) + ((60 - Math.abs(patientAge - 50)) * 0.15)))
  );
  const simulatedClinicalWeight = 100 - simulatedImageWeight;
  const baseRisk = (imageClarity * 0.6) + ((patientAge / 90) * 40);
  const simulatedMalignantProb = Math.min(96, Math.max(6, Math.round(baseRisk)));
  const simulatedUncertainty = (imageClarity < 40) ? 'HIGH' : (imageClarity < 70) ? 'MODERATE' : 'LOW';

  const pipelineSteps = [
    {
      title: 'Dual-View DICOM Ingestion',
      subtitle: 'CC & MLO Mammograms',
      tag: 'Radiological Stream',
      color: 'var(--accent)',
      description: 'Medical mammograms are acquired in two standard orthogonal projections: Craniocaudal (CC, cranial view) and Mediolateral Oblique (MLO, lateral view including pectoral muscle). The system reads standard DICOM tags, inverts monochromatic ranges, normalizes contrast, and crops peripheral air.',
      why: 'A tumor obscured by dense glandular tissue in the CC view is frequently visible in the MLO projection. Processing both views simultaneously mirrors true clinical radiologist practice.'
    },
    {
      title: 'Shared EfficientNetV2-S Backbone',
      subtitle: 'Deep Visual Embeddings (256-d)',
      tag: 'Computer Vision',
      color: 'var(--accent-2)',
      description: 'Both mammographic projections pass through a parameter-shared EfficientNetV2-S convolutional network (pre-trained on ImageNet-21k). Features from both views are combined using masked dual-view pooling with learnable imputation tokens for missing views.',
      why: 'EfficientNetV2-S provides state-of-the-art parameter efficiency and progressive regularization, detecting microcalcification clusters without overfitting on medical cohorts.'
    },
    {
      title: 'Clinical Covariate Encoder',
      subtitle: 'Multi-Layer Perceptron (256-d)',
      tag: 'Clinical Stream',
      color: 'var(--accent-blue)',
      description: 'Patient epidemiological indicators (standardized age, BI-RADS parenchymal density, family history) are encoded via a 2-layer MLP with LayerNorm, GELU non-linearities, and Dropout into the same 256-dimensional latent space.',
      why: 'Pure computer vision models lack demographic context. Patient age is one of the strongest statistical risk multipliers in breast oncology.'
    },
    {
      title: 'Adaptive Modality Gating',
      subtitle: 'Patient-Specific Dynamic Attention',
      tag: 'Multimodal Fusion',
      color: 'var(--warning)',
      description: 'Instead of naive concatenation, an attention gate dynamically computes modality weights W_img and W_clin conditioned on the combined features: z_fused = (W_img * z_img) + (W_clin * z_clin).',
      why: 'If a mammogram suffers from motion blur or high glandular masking, the gate automatically downweights the visual stream and leans on clinical risk indicators, preventing catastrophic errors.'
    },
    {
      title: 'Confidence-Aware Uncertainty',
      subtitle: '15x Monte Carlo Dropout',
      tag: 'Epistemic Safety',
      color: 'var(--success)',
      description: 'Standard models output overconfident single probabilities. CARE-XAI keeps dropout active during inference, executing 15 stochastic forward passes to compute predictive standard deviation (σ) and Shannon entropy.',
      why: 'If the model is guessing near the decision boundary (σ >= 0.08), it generates a HIGH_UNCERTAINTY safety alert, instructing the radiologist to order an ultrasound or tissue biopsy.'
    },
    {
      title: 'Grad-CAM++ Visual Proof',
      subtitle: 'Localized Saliency Attention Maps',
      tag: 'Explainable AI (XAI)',
      color: 'var(--danger)',
      description: 'Generates pixel-level activation heatmaps using second-order gradients at the final convolutional layer of EfficientNetV2. Highlights suspicious tissue margins and microcalcifications.',
      why: 'Eliminates "black-box" skepticism. Clinicians can verify that the AI is focusing on the actual suspicious lesion rather than detector noise, skin folds, or radiographic markers.'
    }
  ];

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '36px 24px 80px' }}>
      
      {/* Header Banner */}
      <section style={{ textAlign: 'center', marginBottom: '44px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '999px', background: 'rgba(167, 60, 255, 0.12)', border: '1px solid rgba(167, 60, 255, 0.3)', marginBottom: '16px' }}>
          <Sparkles size={14} color="var(--accent)" />
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            System Architecture & Clinical Purpose
          </span>
        </div>
        <h1 style={{ fontSize: 'clamp(28px, 4vw, 46px)', fontWeight: 800, letterSpacing: '-0.03em', margin: '0 0 16px', lineHeight: 1.15 }}>
          How <span className="sd-gradient-text">CARE-XAI</span> Works & Why It Matters
        </h1>
        <p style={{ maxWidth: '780px', margin: '0 auto', fontSize: '16px', color: 'var(--text-2)', lineHeight: 1.6 }}>
          A step-by-step walkthrough of how dual-view radiology and structured patient data 
          are fused, calibrated for clinical safety, and visually explained for oncologist decision support.
        </p>
      </section>

      {/* 3 Quick Value Pillars for User/Teacher */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '48px' }}>
        <div className="sd-glass-card" style={{ padding: '24px', borderTop: '3px solid var(--accent)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(167, 60, 255, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Layers size={18} color="var(--accent)" />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>1. Why Multimodal AI?</h3>
          </div>
          <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55, margin: 0 }}>
            Mammography alone has a 15–25% false negative rate in dense breasts. Combining bilateral views (CC + MLO) with patient age and clinical history mimics a senior radiologist’s comprehensive review.
          </p>
        </div>

        <div className="sd-glass-card" style={{ padding: '24px', borderTop: '3px solid var(--warning)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(255, 183, 3, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldCheck size={18} color="var(--warning)" />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>2. Why Confidence-Aware?</h3>
          </div>
          <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55, margin: 0 }}>
            Standard AI models give a single overconfident number (e.g. 90% malignant) even on noisy scans. CARE-XAI tests its own stability via 15 Monte Carlo forward passes to warn doctors when it is uncertain.
          </p>
        </div>

        <div className="sd-glass-card" style={{ padding: '24px', borderTop: '3px solid var(--accent-2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(15, 204, 206, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Eye size={18} color="var(--accent-2)" />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0 }}>3. Why Grad-CAM++ (XAI)?</h3>
          </div>
          <p style={{ fontSize: '13.5px', color: 'var(--text-2)', lineHeight: 1.55, margin: 0 }}>
            Doctors cannot trust a black-box score. Grad-CAM++ highlights the exact pixels of tissue distortion and microcalcifications, providing visual proof that the AI is inspecting genuine pathology.
          </p>
        </div>
      </section>

      {/* Interactive Architecture Pipeline Navigator */}
      <section className="sd-glass-card-glow" style={{ padding: '32px', borderRadius: '20px', marginBottom: '56px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '22px', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
              <GitMerge color="var(--accent-2)" /> Complete Diagnostic Dataflow Pipeline
            </h2>
            <small style={{ color: 'var(--text-3)' }}>Click any stage below to inspect its mathematical formulation and clinical role.</small>
          </div>
          <span className="sd-pill sd-pill-accent">Interactive Pipeline</span>
        </div>

        {/* Step Tabs Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px', marginBottom: '24px' }}>
          {pipelineSteps.map((step, idx) => (
            <button
              key={idx}
              onClick={() => setActiveStep(idx)}
              style={{
                textAlign: 'left',
                padding: '12px 14px',
                borderRadius: '12px',
                background: activeStep === idx ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.02)',
                border: activeStep === idx ? `1px solid ${step.color}` : '1px solid var(--line)',
                cursor: 'pointer',
                color: 'var(--text)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '11px', color: step.color, fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                Stage 0{idx + 1}
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {step.title}
              </div>
            </button>
          ))}
        </div>

        {/* Active Stage Detailed Card */}
        <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '16px', padding: '24px', border: '1px solid var(--line)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <span className="sd-pill" style={{ background: 'rgba(255,255,255,0.05)', color: pipelineSteps[activeStep].color, border: `1px solid ${pipelineSteps[activeStep].color}`, fontSize: '11px', marginRight: '10px' }}>
                {pipelineSteps[activeStep].tag}
              </span>
              <h3 style={{ display: 'inline', fontSize: '20px', fontWeight: 700, color: 'var(--text)' }}>
                {pipelineSteps[activeStep].title} — <span style={{ color: 'var(--text-3)', fontSize: '15px', fontWeight: 500 }}>{pipelineSteps[activeStep].subtitle}</span>
              </h3>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-3)' }}>
              Step {activeStep + 1} of 6
            </div>
          </div>

          <p style={{ fontSize: '14.5px', color: 'var(--text-2)', lineHeight: 1.6, marginBottom: '16px' }}>
            {pipelineSteps[activeStep].description}
          </p>

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', padding: '12px 16px', borderRadius: '10px', background: 'rgba(15, 204, 206, 0.08)', border: '1px solid rgba(15, 204, 206, 0.2)' }}>
            <Info size={18} color="var(--accent-2)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <b style={{ fontSize: '12.5px', color: 'var(--accent-2)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Clinical & Engineering Justification:</b>
              <div style={{ fontSize: '13px', color: 'var(--text)', marginTop: '2px' }}>
                {pipelineSteps[activeStep].why}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Gating & Uncertainty Simulator */}
      <section className="sd-glass-card" style={{ padding: '32px', borderRadius: '20px', marginBottom: '56px' }}>
        <div style={{ marginBottom: '24px' }}>
          <span className="sd-pill sd-pill-cyan" style={{ marginBottom: '10px', display: 'inline-block' }}>
            <Sliders size={12} /> Interactive Simulator
          </span>
          <h2 style={{ fontSize: '24px', fontWeight: 700, margin: '4px 0 8px' }}>
            Test the Adaptive Modality Gate Live
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--text-2)', margin: 0 }}>
            Adjust the sliders below to simulate different clinical patient scenarios. 
            Notice how the model dynamically redistributes weight between radiological imaging and clinical age!
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px', alignItems: 'center' }}>
          
          {/* Controls Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <label style={{ fontSize: '13.5px', fontWeight: 600 }}>
                  Radiological Scan Clarity / Lesion Evidence:
                </label>
                <span className="sd-mono" style={{ color: 'var(--accent)', fontWeight: 700 }}>
                  {imageClarity}% ({imageClarity > 70 ? 'High Detail' : imageClarity > 40 ? 'Moderate Noise' : 'Severe Dense Masking'})
                </span>
              </div>
              <input 
                type="range" 
                min="10" 
                max="95" 
                value={imageClarity} 
                onChange={(e) => setImageClarity(+e.target.value)}
                style={{ width: '100%', accentColor: 'var(--accent)', cursor: 'pointer' }}
              />
              <small style={{ color: 'var(--text-3)', display: 'block', marginTop: '4px' }}>
                Simulates distinct mass vs dense parenchymal background.
              </small>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <label style={{ fontSize: '13.5px', fontWeight: 600 }}>
                  Patient Age:
                </label>
                <span className="sd-mono" style={{ color: 'var(--accent-2)', fontWeight: 700 }}>
                  {patientAge} Years Old
                </span>
              </div>
              <input 
                type="range" 
                min="24" 
                max="82" 
                value={patientAge} 
                onChange={(e) => setPatientAge(+e.target.value)}
                style={{ width: '100%', accentColor: 'var(--accent-2)', cursor: 'pointer' }}
              />
              <small style={{ color: 'var(--text-3)', display: 'block', marginTop: '4px' }}>
                Epidemiological risk baseline increases with age.
              </small>
            </div>

            <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)', fontSize: '12.5px', color: 'var(--text-2)' }}>
              💡 <b>Observation:</b> When image evidence is clear, the Adaptive Gate assigns up to 85%+ weight to the vision stream. When scans are ambiguous or dense, clinical weighting automatically ramps up!
            </div>
          </div>

          {/* Simulation Output Card */}
          <div style={{ background: 'rgba(8, 8, 12, 0.85)', padding: '24px', borderRadius: '16px', border: '1px solid var(--line-accent)' }}>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-3)', marginBottom: '14px' }}>
              Live Adaptive Gate Synthesis
            </div>

            {/* Split Bar */}
            <div style={{ marginBottom: '18px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                <span style={{ color: 'var(--accent)' }}>Image Weight: {simulatedImageWeight}%</span>
                <span style={{ color: 'var(--accent-2)' }}>Clinical Weight: {simulatedClinicalWeight}%</span>
              </div>
              <div style={{ height: '10px', borderRadius: '5px', background: '#222', overflow: 'hidden', display: 'flex' }}>
                <div style={{ width: `${simulatedImageWeight}%`, background: 'var(--accent)', transition: 'width 0.25s ease' }} />
                <div style={{ width: `${simulatedClinicalWeight}%`, background: 'var(--accent-2)', transition: 'width 0.25s ease' }} />
              </div>
            </div>

            {/* Diagnostic Outcome */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '18px' }}>
              <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)' }}>
                <small style={{ color: 'var(--text-3)', display: 'block', marginBottom: '4px' }}>Predicted Risk</small>
                <div style={{ fontSize: '26px', fontWeight: 800, color: simulatedMalignantProb >= 50 ? 'var(--danger)' : 'var(--success)' }}>
                  {simulatedMalignantProb}%
                </div>
                <span style={{ fontSize: '11px', fontWeight: 600, color: simulatedMalignantProb >= 50 ? 'var(--danger)' : 'var(--success)' }}>
                  {simulatedMalignantProb >= 50 ? 'MALIGNANT (BI-RADS 4/5)' : 'BENIGN (BI-RADS 2)'}
                </span>
              </div>

              <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)' }}>
                <small style={{ color: 'var(--text-3)', display: 'block', marginBottom: '4px' }}>MC Uncertainty</small>
                <div style={{ fontSize: '18px', fontWeight: 700, color: simulatedUncertainty === 'LOW' ? 'var(--success)' : simulatedUncertainty === 'MODERATE' ? 'var(--warning)' : 'var(--danger)', marginTop: '4px' }}>
                  {simulatedUncertainty} RISK
                </div>
                <span style={{ fontSize: '11px', color: 'var(--text-3)' }}>
                  {simulatedUncertainty === 'LOW' ? 'Stable over 15 passes' : 'Requires clinical review'}
                </span>
              </div>
            </div>

            <button 
              className="sd-btn sd-btn-accent" 
              onClick={onLaunchWorkstation}
              style={{ width: '100%', height: '42px', fontSize: '13.5px' }}
            >
              Open Diagnostic Workstation with Full Scans <ArrowRight size={15} />
            </button>
          </div>

        </div>
      </section>

      {/* How a Clinician Uses This (Step-by-Step Workflow Guide) */}
      <section className="sd-glass-card" style={{ padding: '32px', borderRadius: '20px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: 700, margin: '0 0 16px' }}>
          Clinician Operating Workflow in 4 Steps
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--accent)', marginBottom: '8px' }}>01</div>
            <h4 style={{ margin: '0 0 6px', fontSize: '15px' }}>Select or Upload Case</h4>
            <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-2)', lineHeight: 1.5 }}>
              Choose a pre-indexed CMMD patient or upload paired CC + MLO DICOM mammograms with patient age.
            </p>
          </div>

          <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--accent-2)', marginBottom: '8px' }}>02</div>
            <h4 style={{ margin: '0 0 6px', fontSize: '15px' }}>Inspect DICOM & Saliency</h4>
            <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-2)', lineHeight: 1.5 }}>
              Examine tissue architecture with window leveling/width controls and toggle Grad-CAM++ to see exact attention heatmaps.
            </p>
          </div>

          <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--warning)', marginBottom: '8px' }}>03</div>
            <h4 style={{ margin: '0 0 6px', fontSize: '15px' }}>Review Gating & Uncertainty</h4>
            <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-2)', lineHeight: 1.5 }}>
              Check calibrated probability, BI-RADS suggestion, and the MC Dropout uncertainty flag to gauge decision stability.
            </p>
          </div>

          <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--success)', marginBottom: '8px' }}>04</div>
            <h4 style={{ margin: '0 0 6px', fontSize: '15px' }}>Record Clinical Audit</h4>
            <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-2)', lineHeight: 1.5 }}>
              Submit concordance (agree/disagree), document clinical rationale, and generate a standardized printable report.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}
