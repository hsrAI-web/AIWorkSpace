import { motion } from 'framer-motion';
import { CaptionRail, Eyebrow, Shot, easeOut } from '../SceneKit';

export function Scene1() {
  return (
    <Shot>
      <div style={{ position: 'absolute', inset: 0, background: '#f3f0e8' }} />
      <div style={{ position: 'absolute', left: '6%', top: '8%', width: '37%', zIndex: 4 }}>
        <Eyebrow>PARTNER OPERATIONS COPILOT</Eyebrow>
        <motion.h1
          className="film-title-xl"
          style={{ marginTop: '4.5vmin', fontSize: '9.1vmin', lineHeight: '.9' }}
          initial={false}
          animate={{ opacity: 1, y: 0, clipPath: 'inset(0 0 0 0)' }}
          transition={{ duration: 0.7, ease: easeOut }}
        >
          ARCHITECTURE<br />FIRST.
        </motion.h1>
        <div className="film-index" style={{ marginTop: '2.4vmin', color: '#8b6a31' }}>
          01 / SYSTEM MAP<br />ARCHITECTURE → FLOW → TECHNICAL DETAILS
        </div>
        <div style={{ marginTop: '3.4vmin', width: '76%', borderTop: '1px solid rgba(32,59,59,.22)', paddingTop: '1.4vmin' }}>
          <span className="film-mono">PARTNER DESK · SYNTHETIC EXAMPLE</span>
        </div>
      </div>
      <motion.div
        style={{
          position: 'absolute', right: '5.5%', top: '8%', width: '52%', height: '69%',
          overflow: 'hidden', border: '1px solid rgba(24,55,52,.25)', borderRadius: '1.4vmin',
          background: '#1e4543', boxShadow: '0 3vmin 8vmin rgba(24,55,52,.2)',
        }}
        initial={{ clipPath: 'inset(3% 5% 3% 5% round 18px)', rotate: 1.2 }}
        animate={{ clipPath: 'inset(0% 0% 0% 0% round 18px)', rotate: 0 }}
        transition={{ duration: 0.75, ease: easeOut }}
      >
        <img className="film-image" src={`${import.meta.env.BASE_URL}images/partner-home.jpg`} alt="" />
        <motion.div
          style={{
            position: 'absolute', left: '35%', top: '48%', width: '31%', height: '9%',
            border: '2px solid #c89d55', borderRadius: '.6vmin',
            boxShadow: '0 0 0 100vmax rgba(23,59,59,.12)',
          }}
          initial={{ opacity: 0, scale: 1.2 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.5, duration: 0.45, ease: easeOut }}
        />
      </motion.div>
      <div style={{ position: 'absolute', left: '6%', bottom: '25%', width: '34%', display: 'grid', gap: '1vmin', zIndex: 3 }}>
        {[
          ['01', 'BROWSER'],
          ['02', 'PUBLIC API'],
          ['03', 'INTERNAL RUNTIME'],
        ].map(([n, label], index) => (
          <motion.div
            key={n}
            style={{
              display: 'grid', gridTemplateColumns: '4.5vmin 1fr', alignItems: 'center',
              borderBottom: '1px solid rgba(32,59,59,.17)', padding: '.75vmin 0',
            }}
            initial={{ opacity: 0, x: -18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.9 + index * 0.32, duration: 0.45, ease: easeOut }}
          >
            <span className="film-index" style={{ color: '#a77d39' }}>{n}</span>
            <span className="film-eyebrow" style={{ color: '#203b3b' }}>{label}</span>
          </motion.div>
        ))}
      </div>
      <motion.div
        style={{
          position: 'absolute', right: '8%', top: '68%', zIndex: 5,
          border: '1px solid #c89d55', borderRadius: '99px', padding: '.8vmin 1.4vmin',
          background: '#fbf8ee', color: '#203b3b', font: '500 1.75vmin var(--font-mono)',
        }}
        initial={false}
        animate={{ x: [0, -12, 0], scale: [1, 1.05, 1] }}
        transition={{ delay: 3, duration: 3, repeat: Infinity, repeatDelay: 1 }}
      >
        DR-2841 · QUESTION
      </motion.div>
      <CaptionRail>
        I’ll explain Partner Operations Copilot: architecture first, then the agent flow, then technical choices and limits. This demo uses synthetic data.
      </CaptionRail>
    </Shot>
  );
}
