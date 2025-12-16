import { GoogleGenAI } from "@google/genai";
import { BeachData } from "../types";

// Safely access process.env to avoid "process is not defined" error in browsers
const getApiKey = () => {
  try {
    return (typeof process !== 'undefined' && process.env?.API_KEY) ? process.env.API_KEY : '';
  } catch (e) {
    return '';
  }
};

const apiKey = getApiKey();

export const generateBeachReport = async (beachData: BeachData): Promise<string> => {
  if (!apiKey) {
    return "API Anahtarı bulunamadı veya yapılandırılmadı. Lütfen sistem yöneticisi ile iletişime geçin.";
  }

  try {
    const ai = new GoogleGenAI({ apiKey });
    
    const prompt = `
      Aşağıdaki verileri analiz et: ${beachData.name}, Konum: ${beachData.location}.
      
      Mevcut İstatistikler:
      - Doluluk: %${beachData.currentStats.occupancy}
      - Kirlilik: %${beachData.currentStats.pollutionLevel} (Kalabalıkla orantılı)
      - Su Kalitesi Endeksi (WQI): ${beachData.currentStats.waterQuality} (Yüksek olması iyidir)
      - Hava Kalitesi Endeksi (AQI): ${beachData.currentStats.airQuality} (Düşük olması iyidir)
      - Sıcaklık: ${beachData.currentStats.temperature}°C

      Geçmiş Veriler (Son 7 Gün):
      ${JSON.stringify(beachData.history)}

      Lütfen turistler için Türkçe olarak 3 cümlelik kısa ve öz bir analiz yaz. Yüzme ve güneşlenme için uygun bir gün olup olmadığına odaklan, özellikle kalabalık ve kirlilik arasındaki dengeyi belirt. Profesyonel ama samimi bir dil kullan.
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
    });

    return response.text || "Analiz şu anda kullanılamıyor.";
  } catch (error) {
    console.error("AI Generation Error:", error);
    return "Ağ hatası veya yapılandırma sorunu nedeniyle şu anda analiz oluşturulamıyor.";
  }
};