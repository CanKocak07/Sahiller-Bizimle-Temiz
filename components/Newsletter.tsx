import React, { useState } from 'react';
import { Mail, CheckCircle, ArrowRight } from 'lucide-react';

const Newsletter: React.FC = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success'>('idle');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setStatus('submitting');
    // Simulate API call
    setTimeout(() => {
      setStatus('success');
      setEmail('');
    }, 1500);
  };

  return (
    <section className="bg-slate-900 py-16 relative overflow-hidden">
      {/* Abstract Background Shapes */}
      <div className="absolute top-0 left-0 w-64 h-64 bg-teal-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>

      <div className="container mx-auto px-4 relative z-10 text-center">
        <div className="max-w-2xl mx-auto">
          <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 text-teal-400">
            <Mail size={32} />
          </div>
          
          <h2 className="text-3xl font-bold text-white mb-4">Gelişmelerden Haberdar Olun</h2>
          <p className="text-slate-400 mb-8 leading-relaxed">
            Antalya sahillerindeki kirlilik raporları, yaklaşan temizlik etkinlikleri ve Caretta Caretta yuvalama dönemleri hakkında haftalık bültenimize abone olun.
          </p>

          {status === 'success' ? (
            <div className="bg-green-500/20 border border-green-500/30 rounded-xl p-4 flex items-center justify-center gap-3 text-green-400 animate-in fade-in slide-in-from-bottom-2">
              <CheckCircle size={20} />
              <span className="font-semibold">Abonelik başarıyla tamamlandı! Teşekkürler.</span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                placeholder="E-posta adresiniz"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-5 py-4 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all"
                required
              />
              <button
                type="submit"
                disabled={status === 'submitting'}
                className="px-8 py-4 bg-teal-600 hover:bg-teal-500 text-white font-bold rounded-xl transition-all shadow-lg hover:shadow-teal-500/25 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {status === 'submitting' ? 'İşleniyor...' : <>Abone Ol <ArrowRight size={18} /></>}
              </button>
            </form>
          )}
          
          <p className="text-slate-600 text-xs mt-4">
            *Asla spam göndermiyoruz. İstediğiniz zaman abonelikten çıkabilirsiniz.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Newsletter;