import { motion } from 'framer-motion';
import { CaptionRail, Eyebrow, Shot, easeOut } from '../SceneKit';

const tools = [
  { label: 'DEAL LOOKUP', id: 'lookup_deal_status', top: '30%' },
  { label: 'QUOTE LOOKUP', id: 'lookup_quote_status', top: '43%' },
  { label: 'REGISTRATION GUIDE', id: 'search_registration_guide', top: '56%' },
];

export function Scene4() {
  return (
    <Shot dark>
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(118deg,#173b3b 0%,#173b3b 47%,#204644 47%,#204644 100%)' }} />
      <div style={{ position: 'absolute', left: '6%', top: '7%', zIndex: 7 }}>
        <Eyebrow>02 — AGENT FLOW / ROUTE BEFORE RESPONSE</Eyebrow>
        <h2 className="film-title" style={{ marginTop: '1.3vmin', fontSize: '6.25vmin' }}>The question takes a path.</h2>
      </div>
      <motion.div
        className="film-card"
        style={{
          position: 'absolute', left: '8%', top: '34%', width: '25%', height: '31%',
          padding: '2.2vmin', background: '#f3f0e8', zIndex: 5,
          display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
          transform: 'rotate(-2.5deg)',
        }}
        initial={{ scale: 0.86, opacity: 0.65, rotate: -8 }}
        animate={{ scale: 1, opacity: 1, rotate: -2.5 }}
        transition={{ duration: 0.6, ease: easeOut }}
      >
        <div className="film-index">DETERMINISTIC GATE</div>
        <div>
          <div style={{ font: '600 4.4vmin/.98 var(--font-display)', color: '#203b3b' }}>Sensitive<br />or routine?</div>
          <div className="film-mono" style={{ color: '#60716c', marginTop: '1.3vmin' }}>CHECK FIRST</div>
        </div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '9%', top: '68%', width: '26%', color: '#f0d59d', zIndex: 6 }}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.5, ease: easeOut }}
      >
        <div className="film-eyebrow" style={{ color: '#d1b573' }}>HUMAN BRANCH</div>
        <div className="film-mono" style={{ marginTop: '.7vmin' }}>SENSITIVE · UNSUPPORTED<br />PRICING · CREDIT · RENEWALS<br />NO MODEL CALL</div>
      </motion.div>
      <motion.div
        className="film-card"
        style={{ position: 'absolute', left: '42%', top: '31%', width: '23%', height: '25%', padding: '1.8vmin', zIndex: 5, background: '#e6ece4', transform: 'rotate(1.3deg)' }}
        initial={{ opacity: 0, scale: 0.84 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.65, duration: 0.6, ease: easeOut }}
      >
        <div className="film-index">ROUTINE PATH</div>
        <div style={{ font: '600 3vmin/1.06 var(--font-display)', color: '#203b3b', marginTop: '1vmin' }}>Planner or<br />agent-selected</div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '42%', top: '61%', color: '#e6ece4', zIndex: 6 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.25, duration: 0.5 }}
      >
        <div className="film-eyebrow" style={{ color: '#d1b573' }}>EXACT ID → DIRECT LOOKUP</div>
        <div className="film-mono" style={{ marginTop: '.6vmin' }}>DR-2841 · Q-73108</div>
      </motion.div>
      {tools.map((tool, index) => (
        <motion.div
          key={tool.id}
          className="film-chip film-chip-dark"
          style={{ position: 'absolute', left: '72%', top: tool.top, width: '24%', padding: '1.1vmin 1.4vmin', zIndex: 6 }}
          initial={{ opacity: 0, x: 28, scale: 0.88 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          transition={{ delay: 1.55 + index * 0.45, duration: 0.55, ease: easeOut }}
        >
          <div className="film-eyebrow" style={{ fontSize: '1.65vmin' }}>{tool.label}</div>
          <div className="film-mono" style={{ opacity: 0.68, marginTop: '.55vmin' }}>{tool.id}</div>
        </motion.div>
      ))}
      <motion.div
        style={{ position: 'absolute', right: '7%', top: '70%', display: 'flex', gap: '1vmin', alignItems: 'center', zIndex: 7 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 3.8, duration: 0.4 }}
      >
        {[0, 1, 2].map((round) => (
          <motion.i
            key={round}
            style={{ width: '1.4vmin', height: '1.4vmin', borderRadius: '50%', background: '#d1b573' }}
            initial={{ scale: 0.3, opacity: 0.3 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 3.9 + round * 0.42, type: 'spring', stiffness: 280 }}
          />
        ))}
        <span className="film-mono" style={{ marginLeft: '.5vmin' }}>MAX 3 TOOL ROUNDS</span>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '43%', top: '76%', zIndex: 8, padding: '.7vmin 1.1vmin', color: '#f4f1e8', borderBottom: '1px solid #d1b573', font: '500 1.5vmin var(--font-mono)' }}
        initial={{ opacity: 0, x: -14 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 19.3, duration: 0.55, ease: easeOut }}
      >
        TOOL RESULTS → CURRENT-TURN EVIDENCE CHECK
      </motion.div>
      <svg viewBox="0 0 1600 900" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 3, pointerEvents: 'none' }}>
        <motion.path d="M510 450 C620 450 610 390 695 390 M695 390 C820 390 850 320 1090 320 M695 390 C820 390 850 430 1120 430 M695 390 C830 410 850 550 1040 560" fill="none" stroke="#d1b573" strokeWidth="4" strokeDasharray="10 11" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 1, duration: 2.9, ease: easeOut }} />
        <motion.path d="M1110 345 C950 260 820 350 695 390" fill="none" stroke="#f3f0e8" strokeWidth="2" strokeDasharray="5 10" initial={{ pathLength: 0, opacity: 0.15 }} animate={{ pathLength: 1, opacity: 0.8 }} transition={{ delay: 4.2, duration: 1.1 }} />
      </svg>
      <CaptionRail>
        Now follow a question. A deterministic gate sends pricing, credit, eligibility, and approval questions to human review without a model call; unsupported data, like renewals, also routes to support. Exact deal or quote IDs go directly to their scoped lookup through a planner. Otherwise, the agent selects a read-only tool. Results return to the agent for at most three tool rounds.
      </CaptionRail>
    </Shot>
  );
}
