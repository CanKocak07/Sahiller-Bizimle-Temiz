import React, { useState } from 'react';
import { Turtle, HelpCircle, CheckCircle2, XCircle, Trophy, ArrowRight, RotateCcw, AlertTriangle } from 'lucide-react';

interface Question {
  id: number;
  text: string;
  options: string[];
  correctAnswer: number; // Index of the correct option
  explanation: string;
}

const QUESTIONS: Question[] = [
  {
    id: 1,
    text: "Caretta Caretta'ların en büyük düşmanı olan ve suyun içinde denizanasına benzediği için yanlışlıkla yuttukları atık nedir?",
    options: [
      "Demir Parçası",
      "Plastik Poşet",
      "Tahta Kasa",
      "Cam Şişe"
    ],
    correctAnswer: 1,
    explanation: "Deniz kaplumbağaları plastik poşetleri denizanası sanarak yerler, bu da sindirim sistemlerini tıkayarak ölümlerine neden olur."
  },
  {
    id: 2,
    text: "Caretta Caretta yavrularının yumurtadan çıkıp denize ulaşabilmesi için sahilde ne YAPILMAMALIDIR?",
    options: [
      "Sessiz olunmalıdır",
      "Uzaktan izlenmelidir",
      "Yapay ışık yakılmamalıdır",
      "Çöpler toplanmalıdır"
    ],
    correctAnswer: 2,
    explanation: "Yavrular denizin parıltısını takip ederler. Yapay ışıklar (fener, flaş, sokak lambası) yönlerini şaşırmalarına ve ölmelerine sebep olur."
  },
  {
    id: 3,
    text: "Bir plastik şişenin denizde tamamen çözünüp yok olması yaklaşık kaç yıl sürer?",
    options: [
      "450 Yıl",
      "50 Yıl",
      "10 Yıl",
      "1 Yıl"
    ],
    correctAnswer: 0,
    explanation: "Plastikler doğada biyolojik olarak parçalanmazlar, sadece mikroplastiklere ayrılarak yüzlerce yıl ekosisteme zarar verirler."
  },
  {
    id: 4,
    text: "\"Mavi Bayrak\" ödülü bir plaj için ne anlama gelir?",
    options: [
      "Plajın çok dalgalı olduğunu",
      "Plajın ücretli olduğunu",
      "Sadece yüzme bilenlerin girebileceğini",
      "Suyun temiz ve çevre standartlarına uygun olduğunu"
    ],
    correctAnswer: 3,
    explanation: "Mavi Bayrak, deniz suyu temizliği, çevre yönetimi ve can güvenliği konularında yüksek standartları temsil eden uluslararası bir ödüldür."
  },
  {
    id: 5,
    text: "Aşağıdakilerden hangisi bireysel olarak deniz kirliliğini önlemek için yapabileceğimiz en etkili harekettir?",
    options: [
      "Tek kullanımlık plastikleri hayatımızdan çıkarmak",
      "Sahilde ateş yakmak",
      "Balıklara ekmek atmak",
      "Denizden taş toplamak"
    ],
    correctAnswer: 0,
    explanation: "Deniz kirliliğinin büyük bir kısmı karasal kaynaklı plastiklerdir. Tüketimi azaltmak kirliliği kaynağında çözer."
  }
];

const Game: React.FC = () => {
  const [gameState, setGameState] = useState<'start' | 'playing' | 'result'>('start');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isAnswerChecked, setIsAnswerChecked] = useState(false);
  const [score, setScore] = useState(0);

  const handleStart = () => {
    setGameState('playing');
    setCurrentQuestionIndex(0);
    setScore(0);
    resetQuestionState();
  };

  const resetQuestionState = () => {
    setSelectedOption(null);
    setIsAnswerChecked(false);
  };

  const handleOptionSelect = (index: number) => {
    if (isAnswerChecked) return;
    setSelectedOption(index);
  };

  const checkAnswer = () => {
    if (selectedOption === null) return;
    
    setIsAnswerChecked(true);
    if (selectedOption === QUESTIONS[currentQuestionIndex].correctAnswer) {
      setScore(prev => prev + 20); // 5 questions * 20 points = 100
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < QUESTIONS.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      resetQuestionState();
    } else {
      setGameState('result');
    }
  };

  // Render Start Screen
  if (gameState === 'start') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 animate-in fade-in duration-500">
        <div className="bg-white max-w-2xl w-full rounded-3xl shadow-xl overflow-hidden border border-teal-100">
          <div className="bg-teal-600 p-8 text-center relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full bg-[url('https://images.unsplash.com/photo-1437622368342-7a3d73a34c8f?q=80&w=2500&auto=format&fit=crop')] bg-cover bg-center opacity-20" />
            <div className="relative z-10">
              <div className="w-24 h-24 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center mx-auto mb-6 border-2 border-white/30">
                <Turtle size={48} className="text-white" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Caretta Dostu Bilgi Yarışması</h1>
              <p className="text-teal-100 text-lg">Denizlerimizi ve sevimli dostlarımızı ne kadar tanıyorsun?</p>
            </div>
          </div>
          
          <div className="p-8">
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-slate-50 p-4 rounded-xl flex items-start gap-3">
                <div className="bg-teal-100 p-2 rounded-lg text-teal-600 mt-1">
                  <HelpCircle size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800">5 Soru</h3>
                  <p className="text-sm text-slate-500">Caretta Carettalar ve deniz kirliliği hakkında.</p>
                </div>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl flex items-start gap-3">
                <div className="bg-orange-100 p-2 rounded-lg text-orange-600 mt-1">
                  <Trophy size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800">Skorunu Gör</h3>
                  <p className="text-sm text-slate-500">Her doğru cevap 20 puan değerindedir.</p>
                </div>
              </div>
            </div>

            <button 
              onClick={handleStart}
              className="w-full bg-teal-600 hover:bg-teal-700 text-white text-xl font-bold py-4 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center gap-2"
            >
              Yarışmaya Başla <ArrowRight size={24} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render Result Screen
  if (gameState === 'result') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 animate-in fade-in zoom-in duration-500">
        <div className="bg-white max-w-lg w-full rounded-3xl shadow-2xl p-8 text-center border-2 border-teal-100">
          <div className="relative mb-8 inline-block">
             <Trophy size={80} className={`mx-auto ${score >= 80 ? 'text-yellow-500' : 'text-slate-300'}`} />
             {score >= 80 && (
               <div className="absolute -top-2 -right-2 bg-yellow-400 text-white text-xs font-bold px-2 py-1 rounded-full animate-bounce">
                 Mükemmel!
               </div>
             )}
          </div>
          
          <h2 className="text-4xl font-bold text-slate-800 mb-2">
            Puanın: <span className="text-teal-600">{score}</span>/100
          </h2>
          
          <p className="text-lg text-slate-600 mb-8 font-medium">
            {score === 100 ? "Harika! Sen gerçek bir deniz koruyucususun! 🌊🐢" : 
             score >= 60 ? "Tebrikler! İyi bir çevre dostusun ama biraz daha öğrenebilirsin. 🌱" : 
             "Teşekkürler! Öğrenilecek çok şey var, denizler seni bekliyor. 📘"}
          </p>

          <div className="flex flex-col gap-3">
            <button 
              onClick={handleStart}
              className="w-full bg-teal-600 text-white font-bold py-3 rounded-xl hover:bg-teal-700 transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw size={20} /> Tekrar Oyna
            </button>
            <button 
              onClick={() => window.location.hash = '/'}
              className="w-full bg-slate-100 text-slate-600 font-bold py-3 rounded-xl hover:bg-slate-200 transition-colors"
            >
              Ana Sayfaya Dön
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render Question Screen
  const currentQuestion = QUESTIONS[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 animate-in fade-in duration-300">
      <div className="max-w-3xl mx-auto">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm font-semibold text-slate-500 mb-2">
            <span>Soru {currentQuestionIndex + 1}/{QUESTIONS.length}</span>
            <span>Puan: {score}</span>
          </div>
          <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-teal-500 transition-all duration-500 ease-out"
              style={{ width: `${((currentQuestionIndex + 1) / QUESTIONS.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
          <div className="p-8">
            <h2 className="text-xl md:text-2xl font-bold text-slate-800 mb-8 leading-relaxed">
              {currentQuestion.text}
            </h2>

            <div className="space-y-4">
              {currentQuestion.options.map((option, index) => {
                let cardClass = "border-2 p-4 rounded-xl flex items-center justify-between cursor-pointer transition-all duration-200 font-medium ";
                
                if (isAnswerChecked) {
                  if (index === currentQuestion.correctAnswer) {
                    cardClass += "border-green-500 bg-green-50 text-green-700";
                  } else if (index === selectedOption) {
                    cardClass += "border-red-500 bg-red-50 text-red-700";
                  } else {
                    cardClass += "border-slate-100 text-slate-400 opacity-60";
                  }
                } else {
                  if (selectedOption === index) {
                    cardClass += "border-teal-500 bg-teal-50 text-teal-700 shadow-md transform scale-[1.02]";
                  } else {
                    cardClass += "border-slate-200 hover:border-teal-300 hover:bg-slate-50 text-slate-700";
                  }
                }

                return (
                  <div 
                    key={index} 
                    onClick={() => handleOptionSelect(index)}
                    className={cardClass}
                  >
                    <span>{option}</span>
                    {isAnswerChecked && index === currentQuestion.correctAnswer && <CheckCircle2 className="text-green-600" />}
                    {isAnswerChecked && index === selectedOption && index !== currentQuestion.correctAnswer && <XCircle className="text-red-600" />}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer / Actions */}
          <div className="bg-slate-50 p-6 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex-1">
              {isAnswerChecked && (
                <div className="flex gap-3 text-sm animate-in slide-in-from-bottom-2">
                  <div className="bg-blue-100 p-2 rounded-lg h-fit text-blue-600">
                    <AlertTriangle size={18} />
                  </div>
                  <p className="text-slate-600 leading-relaxed">
                    <span className="font-bold text-slate-800 block mb-1">Bilgi:</span>
                    {currentQuestion.explanation}
                  </p>
                </div>
              )}
            </div>

            <div className="w-full md:w-auto">
              {!isAnswerChecked ? (
                <button 
                  onClick={checkAnswer}
                  disabled={selectedOption === null}
                  className="w-full md:w-auto px-8 py-3 bg-teal-600 text-white font-bold rounded-xl hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Cevabı Kontrol Et
                </button>
              ) : (
                <button 
                  onClick={nextQuestion}
                  className="w-full md:w-auto px-8 py-3 bg-slate-800 text-white font-bold rounded-xl hover:bg-slate-900 transition-colors flex items-center justify-center gap-2"
                >
                  {currentQuestionIndex === QUESTIONS.length - 1 ? 'Sonucu Gör' : 'Sonraki Soru'} <ArrowRight size={18} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Game;