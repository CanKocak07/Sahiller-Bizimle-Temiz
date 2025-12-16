import React, { useEffect, useState, useRef } from 'react';
import { getAllBeachesData } from '../services/dataService';
import { BeachData } from '../types';
import SummaryCard from '../components/SummaryCard';
import VolunteerSection from '../components/VolunteerSection';
import Newsletter from '../components/Newsletter';
import { MapPin } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [beachData, setBeachData] = useState<BeachData[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Track the current "data block" (2-hour interval index)
  const currentBlockRef = useRef<number>(Math.floor(Date.now() / (1000 * 60 * 60 * 2)));

  const fetchData = () => {
    // Determine which 2-hour block we are in
    const newBlock = Math.floor(Date.now() / (1000 * 60 * 60 * 2));
    
    // If it's a new block (or initial load), we get new data
    // (Note: getAllBeachesData generates random data on every call, 
    // simulating a "live" change)
    if (newBlock !== currentBlockRef.current || beachData.length === 0) {
        currentBlockRef.current = newBlock;
        setBeachData(getAllBeachesData());
    }
    setLoading(false);
  };

  useEffect(() => {
    // Initial fetch
    const timer = setTimeout(() => {
      fetchData();
    }, 800);

    // Check every minute if we entered a new 2-hour block
    const interval = setInterval(() => {
        const checkBlock = Math.floor(Date.now() / (1000 * 60 * 60 * 2));
        if (checkBlock !== currentBlockRef.current) {
            setLoading(true); // Optional: show loading state briefly
            setTimeout(() => fetchData(), 500);
        }
    }, 60000);

    return () => {
        clearTimeout(timer);
        clearInterval(interval);
    };
  }, []);

  return (
    <div className="animate-in fade-in duration-700">
      {/* Hero Section */}
      <section className="relative bg-teal-900 text-white py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 z-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1548574505-5e239809ee19?q=80&w=2568&auto=format&fit=crop')] bg-cover bg-center" />
        <div className="absolute inset-0 z-10 bg-gradient-to-b from-teal-900/80 to-slate-900/90" />
        
        <div className="container mx-auto px-4 relative z-20 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
            Antalya Sahilleri, <span className="text-teal-300">Mercek Altında.</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-200 max-w-2xl mx-auto mb-8 leading-relaxed">
            Akdeniz'in en değerli plajlarında kalabalık oranları, su temizliği ve çevre sağlığının gerçek zamanlı takibi.
          </p>
          <div className="flex justify-center gap-4">
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20">
               <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
               <span className="text-sm font-medium">Canlı Güncelleme</span>
            </div>
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20">
               <MapPin size={16} className="text-teal-300" />
               <span className="text-sm font-medium">5 Lokasyon</span>
            </div>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <section className="container mx-auto px-4 py-12 -mt-10 relative z-30">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-64 bg-slate-200 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {beachData.map((beach) => (
              <SummaryCard key={beach.id} data={beach} />
            ))}
          </div>
        )}
      </section>

      {/* Info Section */}
      <section className="bg-white py-16 border-t border-slate-100">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-slate-800 mb-8">Neden Takip Etmelisiniz?</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="p-6 bg-slate-50 rounded-2xl">
                <div className="w-12 h-12 bg-teal-100 text-teal-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <MapPin />
                </div>
                <h3 className="font-semibold text-lg mb-2">Kalabalık Kontrolü</h3>
                <p className="text-slate-600 text-sm">Karmaşadan uzak durun. Gerçek zamanlı yoğunluk haritası ile aileniz için en sakin noktayı bulun.</p>
              </div>
              <div className="p-6 bg-slate-50 rounded-2xl">
                <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <MapPin />
                </div>
                <h3 className="font-semibold text-lg mb-2">Su Güvenliği</h3>
                <p className="text-slate-600 text-sm">Güvenli bir yüzme deneyimi için su kalitesi endekslerini takip edin ve bilgi sahibi olun.</p>
              </div>
              <div className="p-6 bg-slate-50 rounded-2xl">
                <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <MapPin />
                </div>
                <h3 className="font-semibold text-lg mb-2">Ekolojik Etki</h3>
                <p className="text-slate-600 text-sm">Çevresel limitlere saygı göstererek Antalya'nın doğal güzelliklerini korumamıza yardımcı olun.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Volunteer Section */}
      <VolunteerSection />

      {/* Newsletter Section */}
      <Newsletter />
    </div>
  );
};

export default Dashboard;