import type { CSSProperties, ReactNode } from 'react';
import { motion } from 'framer-motion';

export const easeOut = [0.22, 1, 0.36, 1] as const;

export function Shot({ children, dark = false }: { children: ReactNode; dark?: boolean }) {
  return (
    <motion.section
      className={`film-shot ${dark ? 'film-dark' : ''}`}
      initial={false}
      animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
      exit={{ opacity: 0, scale: 1.045, filter: 'blur(10px)' }}
      transition={{ duration: 0.48, ease: easeOut }}
    >
      {children}
    </motion.section>
  );
}

export function CaptionRail({ children }: { children: ReactNode }) {
  return (
    <motion.div
      className="film-caption"
      role="note"
      aria-label="Narration captions"
      initial={false}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 12 }}
    >
      <span className="film-caption-label">PRESENTER · CAPTIONS</span>
      <div>{children}</div>
    </motion.div>
  );
}

export function Eyebrow({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  return <div className="film-eyebrow" style={style}>{children}</div>;
}

export function Token({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  return (
    <motion.div
      className="film-chip film-mono"
      style={{ display: 'inline-flex', alignItems: 'center', gap: '1vmin', ...style }}
      initial={{ opacity: 0, scale: 0.7, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ delay: 0.6, duration: 0.55, ease: easeOut }}
    >
      <i style={{ width: '.8vmin', height: '.8vmin', borderRadius: '50%', background: 'var(--color-accent)' }} />
      {children}
    </motion.div>
  );
}
