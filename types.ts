export interface Beach {
  id: string;
  name: string;
  location: string;
  image: string;
}

export interface EnvironmentalData {
  date: string;
  occupancy: number; // 0-100%
  waterQuality: number; // 0-100 (WQI), higher is better
  airQuality: number; // 0-500 (AQI), lower is better
  temperature: number; // Celsius
  pollutionLevel: number; // 0-100%, higher is worse (correlated with occupancy)
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