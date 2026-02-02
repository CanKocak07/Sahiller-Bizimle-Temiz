import React, { useState, useEffect } from 'react';
import { BeachData } from '../types';
import { Wind, Droplets, Thermometer, Trash2, RefreshCw, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SummaryCardProps {
  data: BeachData;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ data }) => {
  const navigate = useNavigate();
  const { currentStats } = data;
  const [timeLeft, setTimeLeft] = useState<string>('');
  const [imgSrc, setImgSrc] = useState(data.image);

  // Determine status color based on water quality
  const getQualityColor = (val: number | null) => {
    if (val == null) return 'bg-slate-100 text-slate-600 border-slate-200';
    if (val >= 90) return 'bg-green-100 text-green-700 border-green-200';
    if (val >= 70) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    return 'bg-red-100 text-red-700 border-red-200';
  };

  // Determine color for pollution (High is bad)
  const getPollutionColor = (val: number | null) => {
    if (val == null) return 'text-slate-600';
    if (val < 30) return 'text-green-600';
    if (val < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Countdown logic: Targets the next even hour (e.g., 12:00, 14:00, 16:00)
  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date();
      const target = new Date(now);
      
      // Find next even hour
      const currentHour = now.getHours();
      const nextEvenHour = currentHour + (2 - (currentHour % 2));
      
      target.setHours(nextEvenHour, 0, 0, 0);
      
      // Handle day rollover if needed (though setHours usually handles it, explicit is safer for logic)
      if (target.getTime() <= now.getTime()) {
         target.setHours(target.getHours() + 2);
      }

      const diff = target.getTime() - now.getTime();
      
      if (diff <= 0) return "00:00:00";

      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      const seconds = Math.floor((diff / 1000) % 60);

      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    // Initial set
    setTimeLeft(calculateTimeLeft());

    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div 
      onClick={() => navigate(`/data-center?beach=${data.id}`)}
      className="group relative bg-white rounded-xl shadow-sm hover:shadow-md border border-slate-100 transition-all duration-300 overflow-hidden cursor-pointer"
    >
      <div className="h-36 w-full overflow-hidden relative">
         <div className="absolute inset-0 bg-slate-900/10 group-hover:bg-slate-900/0 transition-colors z-10" />
        <img 
          src={imgSrc} 
          alt={data.name} 
          onError={() => setImgSrc('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80')}
          className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500" 
        />
        
        {/* Next Update Countdown Badge */}
        <div className="absolute top-0 right-0 z-20 bg-slate-900/80 backdrop-blur-sm text-white text-xs font-mono py-1 px-2 rounded-bl-lg flex items-center gap-1.5 border-l border-b border-white/10">
            <RefreshCw size={10} className="animate-spin-slow" style={{ animationDuration: '3s' }} />
            <span>Yenileme: {timeLeft}</span>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent z-20">
          <h3 className="text-white font-bold text-lg leading-tight">{data.name}</h3>
          <p className="text-white/80 text-xs flex items-center gap-1 mt-0.5">
            <Clock size={10} /> Canlı Takip
          </p>
        </div>
      </div>
      
      <div className="p-4 grid grid-cols-2 gap-4">
        {/* Air Quality */}
        <div className="flex flex-col gap-1">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Wind size={12} /> Hava Kalitesi
          </span>
          <span className="font-semibold text-slate-700">{currentStats.airQuality == null ? '-' : currentStats.airQuality}</span>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-amber-500 h-full rounded-full" 
              style={{ width: `${Math.min(100, currentStats.airQuality ?? 0)}%` }}
            />
          </div>
        </div>

        {/* Water Quality */}
        <div className="flex flex-col gap-1">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Droplets size={12} /> Su Kalitesi
          </span>
           <span className={`text-xs font-bold px-2 py-0.5 rounded-full border w-fit ${getQualityColor(currentStats.waterQuality)}`}>
            WQI {currentStats.waterQuality == null ? '-' : currentStats.waterQuality}
          </span>
        </div>

        {/* Temperature */}
        <div className="flex flex-col gap-1">
          <span className="text-xs text-slate-500 flex items-center gap-1">
             <Thermometer size={12} /> Sıcaklık
          </span>
          <span className="font-semibold text-slate-700">{currentStats.temperature == null ? '-' : `${currentStats.temperature}°C`}</span>
        </div>

         {/* Pollution Level */}
         <div className="flex flex-col gap-1">
          <span className="text-xs text-slate-500 flex items-center gap-1">
             <Trash2 size={12} /> Kirlilik
          </span>
          <span className={`font-semibold ${getPollutionColor(currentStats.pollutionLevel)}`}>
            {currentStats.pollutionLevel == null ? '-' : `${currentStats.pollutionLevel}%`}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SummaryCard;