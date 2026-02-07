import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import DataCenter from './pages/DataCenter';
import Game from './pages/Game';
import { getTimeUntilNextTrMidnightMs, getTrDateKey } from './utils/trTime';

const App: React.FC = () => {
  useEffect(() => {
    let timeoutId: number | undefined;
    let lastKey = getTrDateKey();

    const checkAndReload = () => {
      const currentKey = getTrDateKey();
      if (currentKey !== lastKey) {
        window.location.reload();
        return;
      }
      // If we're very close to midnight or timers were delayed, retry soon.
      timeoutId = window.setTimeout(checkAndReload, 10_000);
    };

    const schedule = () => {
      const ms = getTimeUntilNextTrMidnightMs();
      timeoutId = window.setTimeout(checkAndReload, ms + 1500);
    };

    schedule();

    window.addEventListener('focus', checkAndReload);
    return () => {
      if (timeoutId != null) window.clearTimeout(timeoutId);
      window.removeEventListener('focus', checkAndReload);
    };
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans text-slate-900">
      <Header />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/data-center" element={<DataCenter />} />
          <Route path="/game" element={<Game />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};

export default App;