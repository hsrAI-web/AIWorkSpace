import { motion } from 'framer-motion';
import { CaptionRail, Eyebrow, Shot, easeOut } from '../SceneKit';

const layers = [
  {
    n: '01', title: 'BROWSER', stack: 'React · TypeScript · Vite · Wouter',
    left: '5.5%', top: '38%', width: '25%', rotate: -3,
  },
  {
    n: '02', title: 'PUBLIC API', stack: 'Express · OpenAPI · Zod',
    left: '36.5%', top: '29%', width: '27%', rotate: 1.5,
  },
  {
    n: '03', title: 'INTERNAL SERVICE', stack: 'FastAPI · 127.0.0.1:8000',
    left: '69%', top: '20%', width: '25%', rotate: -1.5,
  },
];

export function Scene2() {
  return (
    <Shot dark>
      <div className="film-grid" />
      <div style={{ position: 'absolute', left: '6%', top: '7%', width: '86%' }}>
        <Eyebrow>01 — ARCHITECTURE / THE REQUEST EDGE</Eyebrow>
        <motion.h2 className="film-title" style={{ marginTop: '1.3vmin', fontSize: '6.6vmin' }} initial={false} animate={{ opacity: 1, y: 0 }}>
          One request. <span style={{ color: '#d1b573' }}>Three boundaries.</span>
        </motion.h2>
      </div>
      <motion.div
        style={{
          position: 'absolute', inset: '27% 4% 22%', background: 'rgba(36,74,70,.72)',
          border: '1px solid rgba(244,241,232,.14)', transform: 'skewY(-4deg) rotate(-1deg)',
          transformOrigin: 'center', zIndex: 1,
        }}
        initial={{ scaleX: 0.76, opacity: 0.4 }}
        animate={{ scaleX: 1, opacity: 1 }}
        transition={{ duration: 0.9, ease: easeOut }}
      />
      {layers.map((layer, index) => (
        <motion.div
          key={layer.n}
          className="film-card"
          style={{
            position: 'absolute', left: layer.left, top: layer.top, width: layer.width,
            height: '29%', padding: '2.1vmin', zIndex: 3 + index, rotate: `${layer.rotate}deg`,
            display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
          }}
          initial={{ opacity: 0, y: 22, rotate: `${layer.rotate + 5}deg` }}
          animate={{ opacity: 1, y: 0, rotate: `${layer.rotate}deg` }}
          transition={{ delay: 0.35 + index * 0.35, duration: 0.6, ease: easeOut }}
        >
          <div className="film-index">{layer.n} / LAYER</div>
          <div>
            <div className="film-eyebrow" style={{ color: '#1e4543' }}>{layer.title}</div>
            <div className="film-mono" style={{ marginTop: '1vmin', color: '#60716c' }}>{layer.stack}</div>
          </div>
        </motion.div>
      ))}
      <svg viewBox="0 0 1600 900" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 6, pointerEvents: 'none' }}>
        <motion.path
          d="M330 435 C470 475 500 380 640 382 S900 350 1105 320"
          fill="none" stroke="#d1b573" strokeWidth="4" strokeDasharray="9 12"
          initial={{ pathLength: 0, opacity: 0.35 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ delay: 1.1, duration: 2.2, ease: easeOut }}
        />
        <motion.circle cx="330" cy="435" r="18" fill="#d1b573" initial={{ scale: 0 }} animate={{ scale: [0, 1, 1.12, 1] }} transition={{ delay: 0.25, duration: 0.65 }} />
        <motion.circle cx="640" cy="382" r="11" fill="#1e4543" stroke="#d1b573" strokeWidth="4" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 1.7, duration: 0.4, type: 'spring', stiffness: 280 }} />
        <motion.circle cx="1105" cy="320" r="11" fill="#1e4543" stroke="#d1b573" strokeWidth="4" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 2.3, duration: 0.4, type: 'spring', stiffness: 280 }} />
      </svg>
      <motion.div
        className="film-card"
        style={{ position: 'absolute', right: '7%', top: '57%', width: '28%', padding: '1.5vmin 1.8vmin', zIndex: 7, background: '#e6ece4' }}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 4.3, duration: 0.5, ease: easeOut }}
      >
        <div className="film-index">BOUNDARY</div>
        <div className="film-mono" style={{ color: '#203b3b', marginTop: '.8vmin' }}>NEBIUS CREDENTIAL · SERVER-SIDE ONLY</div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '38%', bottom: '24%', width: '25%', textAlign: 'center', color: '#f4f1e8', zIndex: 4 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 5.2, duration: 0.5 }}
      >
        <div className="film-mono">PUBLIC EDGE → PRIVATE LOOPBACK</div>
      </motion.div>
      <motion.div
        style={{ position: 'absolute', left: '32%', top: '57%', zIndex: 8, padding: '.75vmin 1.15vmin', border: '1px solid #c89d55', borderRadius: '99px', background: '#fbf8ee', color: '#203b3b', font: '500 1.45vmin var(--font-mono)' }}
        initial={{ opacity: 0, x: 0, scale: 0.75 }}
        animate={{ opacity: [0, 1, 1, 0], x: [0, 100, 210], scale: [0.75, 1, 1.35] }}
        transition={{ delay: 16.2, duration: 1.65, ease: easeOut, times: [0, 0.2, 0.72, 1] }}
      >
        REQUEST → LANGGRAPH
      </motion.div>
      <CaptionRail>
        The browser is a React and TypeScript workspace built with Vite and Wouter. An Orval-generated React Query client follows OpenAPI. Public Express validates requests with Zod and in-memory demo caps, then proxies to internal FastAPI on loopback. The browser never calls Nebius; credentials stay server-side.
      </CaptionRail>
    </Shot>
  );
}
