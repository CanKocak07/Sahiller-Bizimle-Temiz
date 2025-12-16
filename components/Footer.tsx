import React, { useState } from 'react';
import { Heart } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 py-8 mt-auto">
      <div className="container mx-auto px-4 text-center">
        <p className="flex items-center justify-center gap-2 text-sm">
          Akdeniz Doğası için Tasarlandı <Heart size={14} className="text-red-500 fill-red-500" />
        </p>
        <p className="text-xs mt-2 text-slate-500">
          © {new Date().getFullYear()} Sahiller Bizimle Temiz. Tüm veriler gösterim amaçlı simüle edilmiştir.
        </p>
      </div>
    </footer>
  );
};

export default Footer;