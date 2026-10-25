import { useCallback, useMemo, useState } from 'react';

const REPEAT_SUFFIX_RE = /_r[12]$/;

export function stripRepeatSuffix(key: string) {
  return key.replace(REPEAT_SUFFIX_RE, '');
}

function rotateFromIndex(durations: Record<string, number>, startIndex: number) {
  const keys = Object.keys(durations);
  if (startIndex <= 0) return durations;
  const result: Record<string, number> = {};
  keys.forEach((_, i) => {
    const key = keys[(startIndex + i) % keys.length];
    result[key] = durations[key];
  });
  return result;
}

function buildLockedDurations(key: string, duration: number) {
  return { [`${key}_r1`]: duration, [`${key}_r2`]: duration };
}

export function useSceneControls(baseDurations: Record<string, number>) {
  const sceneKeys = useMemo(() => Object.keys(baseDurations), [baseDurations]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [locked, setLocked] = useState(false);
  const [paused, setPaused] = useState(false);
  const [muted, setMuted] = useState(false);
  const [mountKey, setMountKey] = useState(0);
  const [tick, setTick] = useState(0);
  const durations = useMemo(() => locked
    ? buildLockedDurations(sceneKeys[activeIndex], baseDurations[sceneKeys[activeIndex]])
    : rotateFromIndex(baseDurations, activeIndex), [locked, activeIndex, sceneKeys, baseDurations]);
  const totalDuration = useMemo(() => Object.values(baseDurations).reduce((a,b) => a+b, 0), [baseDurations]);
  const activeStartTime = useMemo(() => sceneKeys.slice(0, activeIndex).reduce((sum,key) => sum + baseDurations[key], 0), [activeIndex, baseDurations, sceneKeys]);
  const onSceneChange = useCallback((key: string) => {
    const index = sceneKeys.indexOf(stripRepeatSuffix(key));
    if (index >= 0) setActiveIndex(index);
    setTick((value) => value + 1);
  }, [sceneKeys]);
  const jumpTo = useCallback((index: number) => {
    setActiveIndex(index);
    setPaused(false);
    setMountKey((key) => key + 1);
    setTick((value) => value + 1);
  }, []);
  const toggleLock = useCallback(() => {
    setLocked((value) => !value);
    setPaused(false);
    setMountKey((key) => key + 1);
    setTick((value) => value + 1);
  }, []);
  const togglePause = useCallback(() => setPaused((value) => !value), []);
  const toggleMuted = useCallback(() => setMuted((value) => !value), []);
  return {
    sceneKeys, activeIndex, locked, paused, muted, mountKey, tick, durations,
    activeDuration: baseDurations[sceneKeys[activeIndex]] ?? 0,
    activeStartTime, totalDuration, onSceneChange, jumpTo, toggleLock, togglePause, toggleMuted,
  };
}
