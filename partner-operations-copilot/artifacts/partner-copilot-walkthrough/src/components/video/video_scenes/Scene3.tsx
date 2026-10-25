import { motion } from 'framer-motion';
import { CaptionRail, Eyebrow, Shot, easeOut } from '../SceneKit';

const tools = [
  { title: 'DEAL STATUS', name: 'lookup_deal_status', x: '67%', y: '29%' },
  { title: 'QUOTE STATUS', name: 'lookup_quote_status', x: '71%', y: '43%' },
  { title: 'REGISTRATION GUIDE', name: 'search_registration_guide', x: '64%', y: '57%' },
];

export function Scene3() {
  return (
    <Shot dark>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 52% 43%, rgba(56,94,83,.55), transparent 60%)' }} />
      <div style={{ position: 'absolute', left: '6%', top: '7%' }}>
        <Eyebrow>01 — ARCHITECTURE / INTERNAL RUNTIME</Eyebrow>
        <h2 className="film-title" style={{ marginTop: '1.3vmin', fontSize: '6.3vmin' }}>The graph is the coordinator.</h2>
      </div>
      <motion.div
        className="film-card"
        style={{
          position: 'absolute', left: '8%', top: '32%', width: '29%', height: '37%',
          padding: '2.2vmin', background: '#f3f0e8', zIndex: 4, display: 'flex',
          flexDirection: 'column', justifyContent: 'space-between', transform: 'rotate(-2deg)',
        }}
        initial={{ scale: 0.9, opacity: 0.7, rotate: -6 }}
        animate={{ scale: 1, opacity: 1, rotate: -2 }}
        transition={{ duration: 0.7, ease: easeOut }}
      >
        <div className="film-index">INTERNAL FASTAPI SERVICE</div>
        <div>
          <div className="film-eyebrow" style={{ color: '#52716a' }}>LANGGRAPH CONTROL FLOW</div>
          <div style={{ font: '600 5.1vmin/.98 var(--font-display)', color: '#203b3b', marginTop: '1.2vmin' }}>Gate.<br />Plan.<br />Check.</div>
        </div>
        <div className="film-mono" style={{ color: '#60716c' }}>PARTNER + THREAD VALIDATED</div>
      </motion.div>
      <motion.div
        className="film-card"
        style={{ position: 'absolute', left: '41%', top: '31%', width: '21%', height: '22%', padding: '1.8vmin', zIndex: 4, background: '#e6ece4', transform: 'rotate(1.5deg)' }}
        initial={{ opacity: 0, scale: 0.84 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.8, duration: 0.6, ease: easeOut }}
      >
        <div className="film-index">MODEL ADAPTER</div>
        <div style={{ font: '600 2.65vmin/1.08 var(--font-display)', color: '#203b3b', marginTop: '1.25vmin' }}>LangChain<br />→ Nebius Qwen3</div>
        <div className="film-mono" style={{ marginTop: '1vmin', color: '#60716c' }}>TOKEN FACTORY</div>
      </motion.div>
      <div style={{ position: 'absolute', left: '41%', top: '59%', width: '20%', color: '#f4f1e8', zIndex: 4 }}>
        <div className="film-eyebrow" style={{ color: '#d1b573' }}>CONVERSATION STATE</div>
        <div className="film-mono" style={{ marginTop: '.8vmin' }}>POSTGRESQL CHECKPOINTS</div>
        <motion.div style={{ height: '1px', marginTop: '1vmin', background: '#c89d55', transformOrigin: 'left' }} initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 1.6, duration: 0.8 }} />
      </div>
      {tools.map((tool, index) => (
        <motion.div
          key={tool.name}
          className="film-chip film-chip-dark"
          style={{ position: 'absolute', left: tool.x, top: tool.y, width: '26%', padding: '1.15vmin 1.5vmin', zIndex: 5 }}
          initial={{ opacity: 0, x: 20, scale: 0.9 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          transition={{ delay: 1.05 + index * 0.45, duration: 0.55, ease: easeOut }}
        >
          <div className="film-eyebrow" style={{ fontSize: '1.65vmin' }}>{tool.title}</div>
          <div className="film-mono" style={{ opacity: 0.72, marginTop: '.7vmin' }}>{tool.name}</div>
        </motion.div>
      ))}
      <motion.div
        style={{ position: 'absolute', left: '68%', top: '71%', width: '25%', display: 'flex', alignItems: 'center', gap: '1.1vmin', zIndex: 4 }}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.6, duration: 0.55, ease: easeOut }}
      >
        <div style={{ width: '1.5vmin', height: '1.5vmin', borderRadius: '50%', background: '#d1b573', flexShrink: 0 }} />
        <div>
          <div className="film-eyebrow" style={{ color: '#d1b573' }}>SOURCE DATA</div>
          <div className="film-mono" style={{ marginTop: '.6vmin' }}>SHARED SYNTHETIC JSON</div>
        </div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '7%', top: '74%', color: '#c8d4ca', zIndex: 3 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 3.3 }}
      >
        <div className="film-eyebrow">SEPARATE BROWSER STATE</div>
        <div className="film-mono" style={{ marginTop: '.65vmin' }}>SUPPORT REQUESTS → localStorage</div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', right: '7%', bottom: '23%', zIndex: 8, padding: '.8vmin 1.3vmin', border: '1px solid rgba(209,181,115,.6)', color: '#f0dfb7', background: 'rgba(23,59,59,.94)', font: '500 1.45vmin var(--font-mono)' }}
        initial={{ opacity: 0, scale: 0.88, x: 16 }}
        animate={{ opacity: 1, scale: 1, x: 0 }}
        transition={{ delay: 20.1, duration: 0.55, ease: easeOut }}
      >
        PARTNER SCOPE INJECTED INTO EACH TOOL
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '32%', top: '48%', zIndex: 9, padding: '.7vmin 1.2vmin', border: '1px solid #d1b573', borderRadius: '99px', background: '#fbf8ee', color: '#203b3b', font: '500 1.45vmin var(--font-mono)' }}
        initial={{ opacity: 0, scale: 0.6, x: 0, y: 0 }}
        animate={{ opacity: [0, 1, 1, 0], scale: [0.6, 1, 1.2, 1.5], x: [0, 150, 280, 360], y: [0, 0, -35, -55] }}
        transition={{ delay: 22.4, duration: 2.4, ease: easeOut, times: [0, 0.22, 0.72, 1] }}
      >
        QUESTION → GATE
      </motion.div>
      <svg viewBox="0 0 1600 900" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 2, pointerEvents: 'none' }}>
        <motion.path d="M590 430 C690 430 680 345 780 345 M590 440 C690 440 700 475 810 475 M590 450 C685 470 680 580 770 590" fill="none" stroke="#d1b573" strokeWidth="3" strokeDasharray="8 12" initial={{ pathLength: 0, opacity: 0.35 }} animate={{ pathLength: 1, opacity: 0.8 }} transition={{ delay: 1, duration: 2.4, ease: easeOut }} />
        <motion.path d="M1020 350 C910 280 850 340 780 345" fill="none" stroke="#f3f0e8" strokeWidth="2" strokeDasharray="5 10" initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 0.8 }} transition={{ delay: 3.2, duration: 1.1, ease: easeOut }} />
      </svg>
      <CaptionRail>
        FastAPI validates the demo partner and thread ID, then invokes LangGraph. The graph coordinates safety, planning, tools, evidence checks, and conversation checkpoints. LangChain adapts Nebius Token Factory’s Qwen3; PostgreSQL stores graph checkpoints. Three partner-scoped, read-only tools share synthetic JSON with the UI. Support requests stay separately in browser localStorage.
      </CaptionRail>
    </Shot>
  );
}
