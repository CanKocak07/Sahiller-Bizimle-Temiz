import React, { useState } from 'react';
import { BEACHES } from '../constants';
import { Calendar, MapPin, User, Mail, Phone, Send, CheckCircle, HeartHandshake } from 'lucide-react';
import { submitVolunteerSignup } from '../services/formService';

const Volunteer: React.FC = () => {
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
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Volunteer submit failed:', err);
      setStatus('idle');
    }
  };

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 animate-in fade-in zoom-in duration-500">
        <div className="bg-white max-w-lg w-full rounded-2xl shadow-xl p-8 text-center border border-teal-100">
          <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={40} />
          </div>
          <h2 className="text-3xl font-bold text-slate-800 mb-4">Teşekkürler!</h2>
          <p className="text-slate-600 text-lg mb-8">
            <span className="font-semibold text-teal-600">{BEACHES.find(b => b.id === formData.beachId)?.name}</span> temizlik etkinliğine katılma talebiniz alındı. Detaylar için <span className="font-semibold">{formData.email}</span> adresi üzerinden sizinle iletişime geçeceğiz.
          </p>
          <button 
            onClick={() => {
              setStatus('idle');
              setFormData({ name: '', email: '', phone: '', beachId: '', date: '', message: '' });
            }}
            className="bg-teal-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-teal-700 transition-colors w-full"
          >
            Başka Bir Gönüllü Kaydet
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 animate-in fade-in duration-500">
      {/* Hero Header */}
      <div className="bg-teal-900 text-white py-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1618477388954-7852f32655ec?q=80&w=2564&auto=format&fit=crop')] bg-cover bg-center opacity-20" />
        <div className="container mx-auto px-4 relative z-10 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Harekete Katılın</h1>
          <p className="text-teal-100 text-lg max-w-2xl mx-auto">
            Akdeniz'in koruyucusu olun. Bir sahil seçin, bir tarih belirleyin ve Antalya'nın kıyılarını tertemiz tutmamıza yardım edin.
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12 -mt-10 relative z-20">
        <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
          <div className="p-8 md:p-10">
            <div className="flex items-center gap-3 mb-8 pb-6 border-b border-slate-100">
              <div className="bg-teal-100 p-3 rounded-lg text-teal-600">
                <HeartHandshake size={24} />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">Gönüllü Kaydı</h2>
                <p className="text-slate-500 text-sm">Temizlik etkinliğine kaydolmak için aşağıdaki formu doldurun.</p>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Personal Info Group */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Kişisel Bilgiler</h3>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <User size={16} /> Ad Soyad
                    </label>
                    <input 
                      required
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="Adınız Soyadınız"
                      className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Phone size={16} /> Telefon Numarası
                    </label>
                    <input 
                      required
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="+90 555 123 4567"
                      className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                    <Mail size={16} /> E-posta Adresi
                  </label>
                  <input 
                    required
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="ornek@email.com"
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                  />
                </div>
              </div>

              <div className="h-px bg-slate-100 my-6" />

              {/* Event Details Group */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Etkinlik Detayları</h3>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <MapPin size={16} /> Sahil Seçimi
                    </label>
                    <select 
                      required
                      name="beachId"
                      value={formData.beachId}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all bg-white"
                    >
                      <option value="" disabled>Bir konum seçin...</option>
                      {BEACHES.map(beach => (
                        <option key={beach.id} value={beach.id}>{beach.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Calendar size={16} /> Tercih Edilen Tarih
                    </label>
                    <input 
                      required
                      type="date"
                      name="date"
                      value={formData.date}
                      onChange={handleChange}
                      min={new Date().toISOString().split('T')[0]}
                      className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Mesaj (İsteğe Bağlı)</label>
                  <textarea 
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Katılma nedeninizi veya özel durumlarınızı bize iletin..."
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all resize-none"
                  />
                </div>
              </div>

              <button 
                type="submit"
                disabled={status === 'submitting'}
                className="w-full bg-teal-600 text-white font-bold text-lg py-4 rounded-xl shadow-lg hover:bg-teal-700 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-8"
              >
                {status === 'submitting' ? (
                  <>İşleniyor...</>
                ) : (
                  <>
                    <Send size={20} /> Kaydı Tamamla
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Volunteer;