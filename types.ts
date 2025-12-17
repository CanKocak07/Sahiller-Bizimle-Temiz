export interface Beach {
  id: string;
  name: string;
  location: string;
  image: string;
}

export interface EnvironmentalData {
  date: string;
  occupancy: number | null; // 0-100%
  waterQuality: number | null; // 0-100 (WQI), higher is better
  airQuality: number | null; // 0-500 (AQI), lower is better
  temperature: number | null; // Celsius
  pollutionLevel: number | null; // 0-100%, higher is worse (correlated with occupancy)
}

export interface BeachData extends Beach {
  currentStats: EnvironmentalData;
  history: EnvironmentalData[];
}

export enum MetricType {
  OCCUPANCY = 'Doluluk Oranı',
  WATER_QUALITY = 'Su Kalitesi',
  POLLUTION = 'Kirlilik Düzeyi',
  AIR_QUALITY = 'Hava Kalitesi',
  TEMPERATURE = 'Sıcaklık'
}