import { motion } from 'framer-motion';
import { CaptionRail, Eyebrow, Shot, easeOut } from '../SceneKit';

const checks = [
  ['01', 'REQUESTED ID', 'citation must match'],
  ['02', 'EXPECTED SOURCE', 'tool must have run'],
  ['03', 'UNCITED ID', 'block unsupported claim'],
];

export function Scene5() {
  return (
    <Shot>
      <div style={{ position: 'absolute', inset: 0, background: '#f3f0e8' }} />
      <div style={{ position: 'absolute', left: '6%', top: '7%', zIndex: 5 }}>
        <Eyebrow>02 — AGENT FLOW / EVIDENCE BEFORE ANSWER</Eyebrow>
        <h2 className="film-title" style={{ marginTop: '1.25vmin', fontSize: '6.4vmin' }}>No evidence. No partial answer.</h2>
      </div>
      <motion.div
        className="film-card"
        style={{
          position: 'absolute', left: '5%', top: '24%', width: '57%', height: '53%',
          overflow: 'hidden', zIndex: 2, transform: 'rotate(-1deg)', background: '#fffdf7',
        }}
        initial={{ clipPath: 'inset(0 0 0 13%)', rotate: -3 }}
        animate={{ clipPath: 'inset(0 0 0 0%)', rotate: -1 }}
        transition={{ duration: 0.75, ease: easeOut }}
      >
        <img className="film-image" src={`${import.meta.env.BASE_URL}images/partner-help.jpg`} alt="" />
        <div style={{ position: 'absolute', left: '3%', bottom: '3%', padding: '.7vmin 1vmin', background: 'rgba(243,240,232,.94)', border: '1px solid rgba(32,59,59,.15)' }}>
          <span className="film-index">INITIAL SCREEN CAPTURE · NOT A LIVE ANSWER</span>
        </div>
      </motion.div>
      <div style={{ position: 'absolute', right: '6%', top: '25%', width: '29%', zIndex: 4 }}>
        <motion.div
          style={{ padding: '1.5vmin 1.7vmin', background: '#e6ece4', borderLeft: '3px solid #285f4e', marginBottom: '1.2vmin' }}
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.45, ease: easeOut }}
        >
          <div className="film-eyebrow" style={{ color: '#285f4e' }}>SOURCES + TIMESTAMPS</div>
          <div className="film-copy" style={{ marginTop: '.7vmin', fontSize: '1.8vmin' }}>Returned with a visible run trace</div>
        </motion.div>
        {checks.map(([number, title, detail], index) => (
          <motion.div
            key={number}
            style={{ display: 'grid', gridTemplateColumns: '3.8vmin 1fr', gap: '.6vmin', padding: '1.2vmin 0', borderBottom: '1px solid rgba(32,59,59,.17)' }}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 + index * 0.55, duration: 0.4, ease: easeOut }}
          >
            <span className="film-index" style={{ color: '#a77d39' }}>{number}</span>
            <div>
              <div className="film-eyebrow" style={{ color: '#203b3b', fontSize: '1.65vmin' }}>{title}</div>
              <div className="film-mono" style={{ marginTop: '.5vmin', color: '#60716c' }}>{detail}</div>
            </div>
          </motion.div>
        ))}
        <motion.div
          style={{ marginTop: '1.4vmin', padding: '1.2vmin 1.5vmin', border: '1px solid rgba(167,125,57,.35)', color: '#6e572d', font: '500 1.7vmin/1.25 var(--font-mono)' }}
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 2.9, duration: 0.45, ease: easeOut }}
        >
          COVERAGE CHECK ≠ SEMANTIC FACT-CHECK
        </motion.div>
      </div>
      <motion.div
        style={{ position: 'absolute', right: '6%', top: '69%', width: '29%', padding: '1.15vmin 1.4vmin', background: '#f7f2e5', borderLeft: '3px solid #bd9446', zIndex: 5 }}
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 3.4, duration: 0.45, ease: easeOut }}
      >
        <div className="film-eyebrow" style={{ color: '#8b6a31', fontSize: '1.6vmin' }}>MISSING EVIDENCE</div>
        <div className="film-mono" style={{ color: '#6e572d', marginTop: '.55vmin' }}>WITHHOLD · FALLBACK · SUPPORT</div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '42%', top: '75%', width: '18%', color: '#285f4e', zIndex: 6, font: '600 1.45vmin var(--font-mono)', letterSpacing: '.04em' }}
        initial={{ opacity: 0, scale: 0.94 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 15.3, duration: 0.45, ease: easeOut }}
      >
        SOURCE DOTS → HUMAN REVIEW
      </motion.div>
      <svg viewBox="0 0 1600 900" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0, zIndex: 3, width: '100%', height: '100%', pointerEvents: 'none' }}>
        {[0, 1, 2].map((index) => (
          <motion.circle key={index} cx={1000 + index * 48} cy="405" r="18" fill="none" stroke="#bd9446" strokeWidth="3" initial={{ scale: 0.3, opacity: 0 }} animate={{ scale: 1, opacity: [0, 1, 0.55] }} transition={{ delay: 1.3 + index * 0.45, duration: 0.6 }} />
        ))}
        <motion.path d="M1010 575 C1030 665 1120 660 1260 650" fill="none" stroke="#bd9446" strokeWidth="3" strokeDasharray="8 10" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 4.1, duration: 1, ease: easeOut }} />
      </svg>
      <CaptionRail>
        Before display, the graph checks citations for requested IDs, expected tools for obvious question types, and uncited IDs in the draft. The interface shows sources, timestamps, and a trace. This is source coverage, not a full semantic fact-check. Missing evidence withholds partial answers; fallback is used only when it covers the whole request.
      </CaptionRail>
    </Shot>
  );
}
