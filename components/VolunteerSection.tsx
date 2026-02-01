import React, { useState } from 'react';
import { BEACHES } from '../constants';
import { User, Mail, Phone, Calendar, MapPin, Send, CheckCircle, Heart, Users, Globe } from 'lucide-react';
import { submitVolunteerSignup } from '../services/formService';

const VolunteerSection: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    beachId: '',
    date: '',
    message: ''
  });

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success'>('idle');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');

    try {
      await submitVolunteerSignup(formData);
      setStatus('success');
    } catch (err) {
      console.error('Volunteer submit failed:', err);
      setStatus('idle');
    }
  };

  return (
    <section id="volunteer" className="py-20 bg-slate-50 relative">
      <div className="container mx-auto px-4">
        
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-6">Neden Gönüllü Olmalısınız?</h2>
          <p className="text-slate-600 text-lg">
            Antalya'nın eşsiz doğasını korumak sadece bir görev değil, geleceğe bırakılacak en büyük mirastır. İşte harekete geçmeniz için 3 neden:
          </p>
        </div>

        {/* Why Volunteer Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow text-center group">
            <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-teal-100 transition-colors">
              <Heart size={32} className="text-teal-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-3">Doğal Yaşamı Koru</h3>
            <p className="text-slate-600 leading-relaxed">
              Nesli tehlike altındaki Caretta Caretta'ların ve deniz canlılarının yaşam alanlarını temiz tutarak ekosistemin devamlılığına katkıda bulunun.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow text-center group">
            <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-blue-100 transition-colors">
              <Globe size={32} className="text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-3">Geleceğe Miras</h3>
            <p className="text-slate-600 leading-relaxed">
              Sürdürülebilir bir çevre bilinci oluşturarak, çocuklarımıza daha mavi, daha temiz ve yaşanabilir bir Antalya bırakın.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow text-center group">
            <div className="w-16 h-16 bg-orange-50 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-orange-100 transition-colors">
              <Users size={32} className="text-orange-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-3">Toplulukla Buluş</h3>
            <p className="text-slate-600 leading-relaxed">
              Sizin gibi doğa aşığı insanlarla tanışın, sosyalleşin ve birlikte başarmanın verdiği manevi tatmini yaşayın.
            </p>
          </div>
        </div>

        {/* Form Section */}
        <div className="max-w-4xl mx-auto bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-200">
          <div className="grid md:grid-cols-5">
            {/* Form Side Image */}
            <div className="hidden md:block md:col-span-2 relative bg-slate-800">
              <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1595278069441-2cf29f8005a4?q=80&w=1000&auto=format&fit=crop')] bg-cover bg-center opacity-60"></div>
              <div className="absolute inset-0 bg-gradient-to-t from-teal-900/90 to-transparent"></div>
              <div className="relative z-10 p-8 h-full flex flex-col justify-end text-white">
                <h3 className="text-2xl font-bold mb-2">Harekete Geç</h3>
                <p className="text-teal-100 text-sm">Küçük bir adım, büyük bir dalga yaratabilir. Bugün aramıza katılın.</p>
              </div>
            </div>

            {/* Form Content */}
            <div className="md:col-span-3 p-8 md:p-12">
              {status === 'success' ? (
                 <div className="h-full flex flex-col items-center justify-center text-center py-10">
                    <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6 animate-bounce">
                      <CheckCircle size={40} />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-800 mb-2">Harikasınız!</h3>
                    <p className="text-slate-600 mb-8">
                      Gönüllü olma talebiniz bize ulaştı. En kısa sürede sizinle iletişime geçeceğiz.
                    </p>
                    <button 
                      onClick={() => {
                        setStatus('idle');
                        setFormData({ name: '', email: '', phone: '', beachId: '', date: '', message: '' });
                      }}
                      className="text-teal-600 font-semibold hover:text-teal-700 underline"
                    >
                      Yeni bir form gönder
                    </button>
                 </div>
              ) : (
                <>
                  <h3 className="text-2xl font-bold text-slate-800 mb-6">Gönüllü Başvuru Formu</h3>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Ad Soyad</label>
                        <div className="relative">
                          <User size={16} className="absolute left-3 top-3.5 text-slate-400" />
                          <input 
                            required
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Adınız"
                            className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                          />
                        </div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Telefon</label>
                        <div className="relative">
                          <Phone size={16} className="absolute left-3 top-3.5 text-slate-400" />
                          <input 
                            required
                            type="tel"
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                            placeholder="555..."
                            className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-500 uppercase">E-posta</label>
                      <div className="relative">
                        <Mail size={16} className="absolute left-3 top-3.5 text-slate-400" />
                        <input 
                          required
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          placeholder="ornek@email.com"
                          className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Sahil</label>
                        <div className="relative">
                          <MapPin size={16} className="absolute left-3 top-3.5 text-slate-400" />
                          <select 
                            required
                            name="beachId"
                            value={formData.beachId}
                            onChange={handleChange}
                            className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all bg-white appearance-none"
                          >
                            <option value="" disabled>Seçiniz...</option>
                            {BEACHES.map(beach => (
                              <option key={beach.id} value={beach.id}>{beach.name}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Tarih</label>
                        <div className="relative">
                          <Calendar size={16} className="absolute left-3 top-3.5 text-slate-400" />
                          <input 
                            required
                            type="date"
                            name="date"
                            value={formData.date}
                            onChange={handleChange}
                            min={new Date().toISOString().split('T')[0]}
                            className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                          />
                        </div>
                      </div>
                    </div>

                    <button 
                      type="submit"
                      disabled={status === 'submitting'}
                      className="w-full bg-teal-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-teal-700 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
                    >
                      {status === 'submitting' ? 'Gönderiliyor...' : <><Send size={18} /> Kaydı Tamamla</>}
                    </button>
                  </form>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default VolunteerSection;