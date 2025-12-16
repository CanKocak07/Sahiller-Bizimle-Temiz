import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getBeachData } from '../services/dataService';
import { generateBeachReport } from '../services/aiService';
import { BeachData, MetricType } from '../types';
import { BEACHES } from '../constants';
import TrendChart from '../components/TrendChart';
import { BarChart2, Download, Bot } from 'lucide-react';

const DataCenter: React.FC = () => {
  const { search } = useLocation();
  const query = new URLSearchParams(search);
  const initialBeachId = query.get('beach') || 'konyaalti';

  const [selectedBeachId, setSelectedBeachId] = useState(initialBeachId);
  const [selectedMetric, setSelectedMetric] = useState<MetricType>(MetricType.OCCUPANCY);
  const [data, setData] = useState<BeachData | null>(null);
  
  // AI Report State
  const [aiReport, setAiReport] = useState<string>("");
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  useEffect(() => {
    // Reset AI report when beach changes
    setAiReport("");
    const beachData = getBeachData(selectedBeachId);
    setData(beachData);
  }, [selectedBeachId]);

  const handleGenerateReport = async () => {
    if (!data) return;
    setIsGeneratingReport(true);
    const report = await generateBeachReport(data);
    setAiReport(report);
    setIsGeneratingReport(false);
  };

  if (!data) return <div className="p-8 text-center">Veriler yükleniyor...</div>;

  return (
    <div className="min-h-screen bg-slate-50 pb-12 animate-in fade-in duration-500">
      <div className="bg-white border-b border-slate-200 shadow-sm sticky top-16 z-30">
        <div className="container mx-auto px-4 py-4 md:py-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Veri Merkezi</h1>
                    <p className="text-slate-500 text-sm">Tarihsel eğilimler ve analizler</p>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3">
                    <select
                        value={selectedBeachId}
                        onChange={(e) => setSelectedBeachId(e.target.value)}
                        className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-teal-500 focus:border-teal-500 block w-full p-2.5"
                    >
                        {BEACHES.map(b => (
                            <option key={b.id} value={b.id}>{b.name}</option>
                        ))}
                    </select>

                     <select
                        value={selectedMetric}
                        onChange={(e) => setSelectedMetric(e.target.value as MetricType)}
                        className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-teal-500 focus:border-teal-500 block w-full p-2.5"
                    >
                        {Object.values(MetricType).map(m => (
                            <option key={m} value={m}>{m}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Chart Area */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <BarChart2 className="text-teal-600" size={20}/>
                            <h2 className="text-lg font-semibold text-slate-800">7 Günlük {selectedMetric} Eğilimi</h2>
                        </div>
                        <span className="text-xs font-mono text-slate-400 bg-slate-100 px-2 py-1 rounded">
                            Son Güncelleme: {new Date().toLocaleTimeString('tr-TR')}
                        </span>
                    </div>
                    
                    <TrendChart data={data.history} metric={selectedMetric} />
                </div>

                {/* AI Analysis Section */}
                 <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-2xl border border-indigo-100 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Bot size={100} />
                    </div>
                    <div className="relative z-10">
                         <div className="flex items-center justify-between mb-4">
                            <h3 className="font-bold text-indigo-900 flex items-center gap-2">
                                <Bot size={20} className="text-indigo-600"/>
                                Yapay Zeka Çevre Analizi
                            </h3>
                             {!aiReport && (
                                <button 
                                    onClick={handleGenerateReport}
                                    disabled={isGeneratingReport}
                                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isGeneratingReport ? 'Analiz Ediliyor...' : 'Rapor Oluştur'}
                                </button>
                             )}
                        </div>
                        
                        {isGeneratingReport && (
                             <div className="space-y-2 animate-pulse">
                                <div className="h-4 bg-indigo-200 rounded w-3/4"></div>
                                <div className="h-4 bg-indigo-200 rounded w-1/2"></div>
                            </div>
                        )}

                        {aiReport && (
                            <div className="bg-white/60 p-4 rounded-xl border border-indigo-100">
                                <p className="text-indigo-800 text-sm leading-relaxed whitespace-pre-line">
                                    {aiReport}
                                </p>
                                <button 
                                    onClick={handleGenerateReport} 
                                    className="text-xs text-indigo-500 hover:text-indigo-700 mt-2 font-medium"
                                >
                                    Analizi Yenile
                                </button>
                            </div>
                        )}
                        {!aiReport && !isGeneratingReport && (
                             <p className="text-sm text-indigo-600/70">
                                Mevcut çevresel eğilimleri analiz etmek ve turistler için bir özet almak amacıyla Gemini AI kullanmak için yukarıdaki butona tıklayın.
                            </p>
                        )}
                    </div>
                </div>
            </div>

            {/* Side Stats */}
            <div className="space-y-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                     <h3 className="font-semibold text-slate-800 mb-4">Anlık Özet</h3>
                     <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                            <span className="text-sm text-slate-600">Durum</span>
                            <span className="text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded">Açık</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                             <span className="text-sm text-slate-600">Doluluk Oranı</span>
                             <span className="text-sm font-bold text-slate-800">{data.currentStats.occupancy}%</span>
                        </div>
                         <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                             <span className="text-sm text-slate-600">Kirlilik Düzeyi</span>
                             <span className="text-sm font-bold text-violet-600">{data.currentStats.pollutionLevel}%</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                             <span className="text-sm text-slate-600">Su Kalitesi</span>
                             <span className="text-sm font-bold text-teal-600">{data.currentStats.waterQuality} WQI</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                             <span className="text-sm text-slate-600">Sıcaklık</span>
                             <span className="text-sm font-bold text-slate-800">{data.currentStats.temperature}°C</span>
                        </div>
                     </div>
                </div>

                <div className="bg-teal-700 text-white p-6 rounded-2xl shadow-lg relative overflow-hidden">
                     <div className="relative z-10">
                        <h3 className="font-bold text-lg mb-2">Verileri Dışa Aktar</h3>
                        <p className="text-teal-100 text-sm mb-4">Araştırma amacıyla son 30 günün çevre kayıtlarını indirin.</p>
                        <button className="flex items-center gap-2 bg-white text-teal-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-teal-50 transition-colors w-full justify-center">
                            <Download size={16} /> CSV İndir
                        </button>
                     </div>
                     <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-teal-500 rounded-full opacity-20" />
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default DataCenter;