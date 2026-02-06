import React, { useEffect, useMemo, useState } from 'react';
import { formatDuration, getTimeUntilNextTrMidnightMs } from '../utils/trTime';

type Props = {
  className?: string;
  showSeconds?: boolean;
  prefix?: string;
};

const UpdateCountdown: React.FC<Props> = ({ className, showSeconds = false, prefix = 'Sonraki güncelleme' }) => {
  const [remainingMs, setRemainingMs] = useState(() => getTimeUntilNextTrMidnightMs());

  const tickMs = showSeconds ? 1000 : 30_000;

  useEffect(() => {
    const t = setInterval(() => {
      setRemainingMs(getTimeUntilNextTrMidnightMs());
    }, tickMs);
    return () => clearInterval(t);
  }, [tickMs]);

  const text = useMemo(() => formatDuration(remainingMs, { showSeconds }), [remainingMs, showSeconds]);

  return (
    <span className={className} title="Günlük güncelleme saati: 00:00 TR">
      {prefix}: {text}
    </span>
  );
};

export default UpdateCountdown;
