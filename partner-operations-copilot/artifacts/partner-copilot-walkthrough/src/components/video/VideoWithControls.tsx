import { useCallback, useEffect, useRef, useState } from 'react';
import { ChevronDown, ChevronUp, Pause, Play, Repeat, Volume2, VolumeX } from 'lucide-react';
import VideoTemplate, { SCENE_DURATIONS } from './VideoTemplate';
import { useSceneControls } from './useSceneControls';

const SCENE_DETAILS: Record<string, { title: string; filePath: string }> = {
  question: { title: 'Architecture overview', filePath: 'src/components/video/video_scenes/Scene1.tsx' },
  api: { title: 'Public and internal architecture', filePath: 'src/components/video/video_scenes/Scene2.tsx' },
  graph: { title: 'Agent runtime architecture', filePath: 'src/components/video/video_scenes/Scene3.tsx' },
  flow: { title: 'Question flow', filePath: 'src/components/video/video_scenes/Scene4.tsx' },
  evidence: { title: 'Evidence and human boundary', filePath: 'src/components/video/video_scenes/Scene5.tsx' },
  limits: { title: 'Technical details and limits', filePath: 'src/components/video/video_scenes/Scene6.tsx' },
};

function announceSceneSelection(index: number, sceneKeys: string[]) {
  const key = sceneKeys[index];
  const detail = SCENE_DETAILS[key];
  if (!detail?.filePath) return;
  window.parent.postMessage({
    type: 'REPLIT_VIDEO_SCENE_SELECTED',
    payload: { sceneIndex: index, sceneCount: sceneKeys.length, sceneTitle: detail.title, filePath: detail.filePath, lineNumber: 1 },
  }, '*');
}

function formatTime(ms: number) {
  const seconds = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}

function PlaybackStatus({ sceneKeys, activeIndex, activeDuration, activeStartTime, totalDuration, tick, paused, onJumpTo }: {
  sceneKeys: string[]; activeIndex: number; activeDuration: number; activeStartTime: number;
  totalDuration: number; tick: number; paused: boolean; onJumpTo: (index: number) => void;
}) {
  const [elapsed, setElapsed] = useState(0);
  const elapsedBaseRef = useRef(0);
  useEffect(() => { setElapsed(0); elapsedBaseRef.current = 0; }, [tick]);
  useEffect(() => {
    if (paused) return;
    const started = performance.now();
    const id = window.setInterval(() => setElapsed(elapsedBaseRef.current + performance.now() - started), 60);
    return () => { window.clearInterval(id); elapsedBaseRef.current += performance.now() - started; };
  }, [tick, paused]);
  const progress = activeDuration ? Math.min(1, elapsed / activeDuration) : 0;
  const totalElapsed = Math.min(totalDuration, activeStartTime + Math.min(elapsed, activeDuration));
  return (
    <>
      <div className="video-progress">
        {sceneKeys.map((key, index) => (
          <button key={key} aria-label={`Jump to scene ${index + 1}`} aria-current={activeIndex === index ? 'true' : undefined} onClick={() => onJumpTo(index)}>
            <span style={{ width: `${index < activeIndex ? 100 : index === activeIndex ? progress * 100 : 0}%` }} />
          </button>
        ))}
      </div>
      <span className="video-count">{activeIndex + 1}/{sceneKeys.length}</span>
      <span className="video-timer" role="timer">{formatTime(totalElapsed)} / {formatTime(totalDuration)}</span>
    </>
  );
}

export default function VideoWithControls() {
  const isIframed = typeof window !== 'undefined' && window.self !== window.top;
  const {
    sceneKeys, activeIndex, locked, paused, muted, mountKey, tick, durations,
    activeDuration, activeStartTime, totalDuration, onSceneChange, jumpTo,
    toggleLock, togglePause, toggleMuted,
  } = useSceneControls(SCENE_DURATIONS);
  const [collapsed, setCollapsed] = useState(false);
  const [hovering, setHovering] = useState(false);
  const [tapPinned, setTapPinned] = useState(false);
  const sensorRef = useRef<HTMLDivElement | null>(null);
  const handleJumpTo = useCallback((index: number) => {
    jumpTo(index);
    announceSceneSelection(index, sceneKeys);
  }, [jumpTo, sceneKeys]);
  useEffect(() => {
    if (!paused) return;
    const frozen = document.getAnimations().filter((animation) => animation.playState === 'running');
    frozen.forEach((animation) => animation.pause());
    return () => frozen.forEach((animation) => animation.play());
  }, [paused]);
  useEffect(() => {
    if (!(collapsed && tapPinned)) return;
    const onDown = (event: PointerEvent) => {
      if (event.pointerType !== 'mouse' && sensorRef.current && !sensorRef.current.contains(event.target as Node)) setTapPinned(false);
    };
    document.addEventListener('pointerdown', onDown);
    return () => document.removeEventListener('pointerdown', onDown);
  }, [collapsed, tapPinned]);
  if (!isIframed) return <VideoTemplate />;
  const visible = !collapsed || hovering || tapPinned;
  return (
    <div className="video-with-controls">
      <VideoTemplate key={mountKey} durations={durations} loop paused={paused} muted={muted} onSceneChange={onSceneChange} />
      <div ref={sensorRef} className="video-sensor" onPointerEnter={(event) => { if (event.pointerType === 'mouse') setHovering(true); }} onPointerLeave={(event) => { if (event.pointerType === 'mouse') setHovering(false); }} onPointerDown={(event) => { if (event.pointerType !== 'mouse' && collapsed) setTapPinned(true); }}>
        <div className="video-sensor-spacer" />
        <div className={`video-control-bar ${visible ? 'is-visible' : ''}`} aria-hidden={!visible}>
          <button aria-label={paused ? 'Play' : 'Pause'} title={paused ? 'Play' : 'Pause'} onClick={togglePause}>{paused ? <Play /> : <Pause />}</button>
          <button aria-label={locked ? 'Loop current scene: on' : 'Loop current scene: off'} aria-pressed={locked} className={locked ? 'control-active' : ''} onClick={toggleLock}><Repeat /></button>
          <button aria-label={muted ? 'Unmute' : 'Mute'} onClick={toggleMuted}>{muted ? <VolumeX /> : <Volume2 />}</button>
          <i className="control-divider" />
          <PlaybackStatus sceneKeys={sceneKeys} activeIndex={activeIndex} activeDuration={activeDuration} activeStartTime={activeStartTime} totalDuration={totalDuration} tick={tick} paused={paused} onJumpTo={handleJumpTo} />
          <button aria-label={collapsed ? 'Show controls' : 'Hide controls'} aria-expanded={!collapsed} onClick={() => { setCollapsed((value) => !value); setHovering(false); setTapPinned(false); }}>{collapsed ? <ChevronUp /> : <ChevronDown />}</button>
        </div>
      </div>
      <style>{`
        .video-with-controls{position:relative;width:100%;height:100vh;overflow:hidden}
        .video-sensor{position:absolute;z-index:50;left:0;right:0;bottom:0;height:25%;display:flex;flex-direction:column;justify-content:flex-end}
        .video-sensor-spacer{flex:1}
        .video-control-bar{display:flex;align-items:center;gap:1.1vmin;padding:1.2vmin 1.8vmin;background:rgba(15,35,34,.78);backdrop-filter:blur(12px);transform:translateY(100%);opacity:0;pointer-events:none;transition:transform .2s ease,opacity .2s ease;color:#f3f0e8}
        .video-control-bar.is-visible{transform:translateY(0);opacity:1;pointer-events:auto}
        .video-control-bar>button{width:5.6vmin;height:5.6vmin;min-width:38px;min-height:38px;border:0;border-radius:.8vmin;background:transparent;color:rgba(243,240,232,.74);display:grid;place-items:center;cursor:pointer}
        .video-control-bar>button:hover,.video-control-bar>button.control-active{background:rgba(255,255,255,.13);color:white}
        .video-control-bar>button svg{width:2.7vmin;height:2.7vmin;min-width:19px;min-height:19px}
        .control-divider{width:1px;height:3.6vmin;background:rgba(255,255,255,.2)}
        .video-progress{display:flex;align-items:center;gap:.55vmin;flex:1}
        .video-progress button{position:relative;padding:0;border:0;height:1.2vmin;min-height:8px;flex:1;overflow:hidden;border-radius:99px;background:rgba(255,255,255,.22);cursor:pointer}
        .video-progress button span{position:absolute;inset:0 auto 0 0;background:#d1b573;border-radius:inherit}
        .video-count,.video-timer{font:500 1.45vmin var(--font-mono);color:rgba(243,240,232,.8);white-space:nowrap}
        .video-timer{min-width:11ch;text-align:right}
      `}</style>
    </div>
  );
}
