import React, { useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Waves, HeartHandshake, Gamepad2 } from 'lucide-react';

const Header: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const toggleMenu = () => setIsOpen(!isOpen);

  const handleVolunteerClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsOpen(false);
    
    // If we are not on the homepage, navigate there first
    if (location.pathname !== '/') {
      navigate('/');
      // Timeout to allow navigation to complete before scrolling
      setTimeout(() => {
        const element = document.getElementById('volunteer');
        element?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      // If already on homepage, just scroll
      const element = document.getElementById('volunteer');
      element?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const navClasses = ({ isActive }: { isActive: boolean }) =>
    `text-sm font-medium transition-colors duration-200 ${
      isActive ? 'text-teal-600' : 'text-slate-600 hover:text-teal-500'
    }`;

  const buttonClasses = 
    `px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 cursor-pointer bg-teal-600 text-white hover:bg-teal-700 shadow-md hover:shadow-lg`;

  return (
    <header className="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="container mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-teal-600 p-2 rounded-lg text-white">
            <Waves size={24} />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-teal-700 to-cyan-600 bg-clip-text text-transparent hidden sm:inline-block">
            Sahiller Bizimle Temiz
          </span>
          <span className="text-xl font-bold bg-gradient-to-r from-teal-700 to-cyan-600 bg-clip-text text-transparent sm:hidden">
            SBT
          </span>
        </div>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          <NavLink to="/" className={navClasses}>
            Ana Sayfa
          </NavLink>
          <NavLink to="/data-center" className={navClasses}>
            Veri Merkezi
          </NavLink>
          <NavLink to="/game" className={navClasses}>
             <div className="flex items-center gap-1">
               <Gamepad2 size={18} /> Oyun
             </div>
          </NavLink>
          <a onClick={handleVolunteerClick} href="/#volunteer" className={buttonClasses}>
            <HeartHandshake size={16} /> Gönüllü Ol
          </a>
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-md"
          onClick={toggleMenu}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Nav */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-slate-100 px-4 py-4 shadow-lg animate-in slide-in-from-top-2">
          <nav className="flex flex-col gap-4">
            <NavLink
              to="/"
              className={navClasses}
              onClick={() => setIsOpen(false)}
            >
              Ana Sayfa
            </NavLink>
            <NavLink
              to="/data-center"
              className={navClasses}
              onClick={() => setIsOpen(false)}
            >
              Veri Merkezi
            </NavLink>
            <NavLink
              to="/game"
              className={navClasses}
              onClick={() => setIsOpen(false)}
            >
               <div className="flex items-center gap-2">
                <Gamepad2 size={18} /> Oyun
               </div>
            </NavLink>
            <a
              onClick={handleVolunteerClick}
              href="/#volunteer"
              className="flex items-center gap-2 text-teal-600 font-semibold cursor-pointer"
            >
              <HeartHandshake size={16} /> Gönüllü Ol
            </a>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;