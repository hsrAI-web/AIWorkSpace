import { motion } from 'framer-motion';
import { CaptionRail, Eyebrow, Shot, easeOut } from '../SceneKit';

const reviewFiles = [
  ['GRAPH', 'src/partner_agent_graph/graph.py'],
  ['TOOLS', 'src/partner_agent_graph/tools.py'],
  ['API', 'src/partner_agent_graph/api.py'],
  ['DOCS', 'docs/partner-copilot-explainer/README.md'],
];

export function Scene6() {
  return (
    <Shot>
      <div style={{ position: 'absolute', inset: 0, display: 'grid', gridTemplateColumns: '43% 57%' }}>
        <div style={{ background: '#f3f0e8' }} />
        <div style={{ background: '#173b3b' }} />
      </div>
      <div style={{ position: 'absolute', left: '6%', top: '7%', width: '80%', zIndex: 6 }}>
        <Eyebrow>SENSITIVE → HUMAN / IMPLEMENTATION LIMITS</Eyebrow>
        <h2 className="film-title" style={{ width: '37%', marginTop: '1.1vmin', fontSize: '4.9vmin', lineHeight: '.98' }}>A human owns<br />the write.</h2>
      </div>
      <motion.div
        className="film-card"
        style={{ position: 'absolute', left: '7%', top: '28%', width: '33%', height: '39%', padding: '2vmin', zIndex: 4, transform: 'rotate(-2deg)' }}
        initial={{ opacity: 0.6, scale: 0.92, rotate: -6, x: 0 }}
        animate={{ opacity: 1, scale: 1, rotate: -2, x: [0, 0, 20] }}
        transition={{ delay: 0.45, duration: 4.5, ease: easeOut, times: [0, 0.72, 1] }}
      >
        <div className="film-index">SUPPORT REQUEST / DRAFT</div>
        <div style={{ height: 1, background: 'rgba(32,59,59,.16)', margin: '1.35vmin 0' }} />
        <div style={{ font: '600 2.6vmin/1.12 var(--font-display)', color: '#203b3b' }}>Partner reviews<br />then explicitly saves</div>
        <motion.div
          style={{ position: 'absolute', right: '1.8vmin', bottom: '1.7vmin', padding: '.8vmin 1.2vmin', background: '#285f4e', color: '#f4f1e8', borderRadius: '.5vmin', font: '500 1.45vmin var(--font-mono)' }}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 1.2, type: 'spring', stiffness: 280 }}
        >
          EXPLICIT SAVE
        </motion.div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '10%', top: '70%', width: '22%', padding: '1vmin 1.3vmin', background: '#e6ece4', zIndex: 4 }}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.5, duration: 0.45, ease: easeOut }}
      >
        <div className="film-eyebrow" style={{ color: '#285f4e', fontSize: '1.65vmin' }}>BROWSER localStorage</div>
        <div className="film-mono" style={{ color: '#60716c', marginTop: '.6vmin' }}>SAME BROWSER ONLY</div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '33%', top: '70%', width: '7%', height: '6%', border: '1px solid rgba(189,148,70,.65)', borderRadius: '.6vmin', display: 'grid', placeItems: 'center', color: '#8b6a31', zIndex: 4, background: 'rgba(243,240,232,.45)' }}
        initial={{ opacity: 0, scale: 0.86 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 3.1, duration: 0.45, ease: easeOut }}
      >
        <span className="film-mono" style={{ fontSize: '1.1vmin', textAlign: 'center' }}>OTHER<br />DEVICE</span>
        <i style={{ position: 'absolute', left: '-10%', top: '50%', width: '120%', height: '1px', background: '#bd9446', transform: 'rotate(-28deg)' }} />
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '39%', top: '44%', height: '25%', width: '1px', background: '#bd9446', transformOrigin: 'top', zIndex: 3 }}
        initial={{ scaleY: 0 }}
        animate={{ scaleY: 1 }}
        transition={{ delay: 1.6, duration: 0.65 }}
      />
      <motion.div
        style={{ position: 'absolute', left: '43%', top: '31%', width: '50%', zIndex: 4 }}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4, duration: 0.6, ease: easeOut }}
      >
        <div className="film-eyebrow" style={{ color: '#d1b573' }}>CURRENT IMPLEMENTATION</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1vmin', marginTop: '1.5vmin' }}>
          {[
            'READ-ONLY TOOLS',
            'PARTNER-SCOPED LOOKUPS',
            'POSTGRESQL CHECKPOINTS',
            'BOUNDED RECOVERY',
          ].map((value, index) => (
            <motion.div
              key={value}
              style={{ padding: '1.1vmin 1.25vmin', border: '1px solid rgba(244,241,232,.2)', color: '#f4f1e8', font: '500 1.7vmin var(--font-mono)' }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.65 + index * 0.28, duration: 0.4 }}
            >
              {value}
            </motion.div>
          ))}
        </div>
        <motion.div
          style={{ marginTop: '1.6vmin', padding: '1.4vmin 1.6vmin', background: 'rgba(243,240,232,.08)', borderLeft: '3px solid #bd9446', color: '#f0dfb7', font: '500 1.75vmin/1.6 var(--font-mono)' }}
          initial={{ opacity: 0, scaleX: 0.9, transformOrigin: 'left' }}
          animate={{ opacity: 1, scaleX: 1 }}
          transition={{ delay: 11.1, duration: 0.5, ease: easeOut }}
        >
          SALESFORCE NOT CONNECTED<br />
          NO CRM WRITES<br />
          DEMO ROLE ≠ SECURE AUTHENTICATION
        </motion.div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '44%', top: '65%', width: '49%', zIndex: 5 }}
        initial={{ opacity: 0, x: 28 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 13.4, duration: 0.65, ease: easeOut }}
      >
        <div className="film-index" style={{ color: '#d1b573' }}>REVIEW THE IMPLEMENTATION</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '.65vmin', marginTop: '.65vmin' }}>
          {reviewFiles.map(([tag, path]) => (
            <div key={tag} className="film-chip film-chip-dark" style={{ padding: '.65vmin .8vmin', overflow: 'hidden', whiteSpace: 'nowrap', color: '#f4f1e8' }}>
              <span className="film-mono" style={{ fontSize: '1.25vmin' }}>{tag} · {path}</span>
            </div>
          ))}
        </div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', right: '8%', top: '21%', padding: '.8vmin 1.25vmin', border: '1px solid #c89d55', borderRadius: '99px', color: '#203b3b', background: '#fbf8ee', font: '500 1.5vmin var(--font-mono)', zIndex: 8 }}
        initial={{ scale: 1, opacity: 1, x: 0 }}
        animate={{ scale: [1, 1, 1.55, 3.4], opacity: [1, 1, 0.8, 0], x: [0, 0, -6, -38] }}
        transition={{ delay: 19.85, duration: 2.1, ease: easeOut, times: [0, 0.3, 0.68, 1] }}
      >
        DR-2841
      </motion.div>
      <CaptionRail>
        For sensitive topics, partners review and explicitly save support requests. Staff can assign and respond in the same browser; requests do not sync across devices. Tools are read-only and scoped, but Salesforce is not connected, there are no CRM writes, and demo-role switching is not secure authentication. This is a demo, not a production portal.
      </CaptionRail>
    </Shot>
  );
}
