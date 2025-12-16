import { BeachData, EnvironmentalData } from '../types';
import { BEACHES } from '../constants';

// Helper to generate a random number within a range
const random = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

// Helper to smooth data to look like realistic trends rather than white noise
const smoothData = (prev: number, min: number, max: number, volatility: number): number => {
  const change = random(-volatility, volatility);
  let next = prev + change;
  if (next < min) next = min + random(0, volatility);
  if (next > max) next = max - random(0, volatility);
  return next;
};

export const generateHistoricalData = (days: number): EnvironmentalData[] => {
  const data: EnvironmentalData[] = [];
  const today = new Date();
  
  // Initial seed values
  let currentOccupancy = 45;
  let currentWaterQuality = 85;
  let currentAirQuality = 30;
  let currentTemp = 28;

  for (let i = days; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    // Simulate daily fluctuations
    currentOccupancy = smoothData(currentOccupancy, 10, 95, 15);
    currentWaterQuality = smoothData(currentWaterQuality, 60, 98, 5);
    currentAirQuality = smoothData(currentAirQuality, 10, 80, 10);
    currentTemp = smoothData(currentTemp, 24, 35, 2);

    // Calculate pollution based on occupancy (Correlation: More people ~ More pollution)
    // Base pollution + (Occupancy factor) + Random variance
    let pollution = 10 + (currentOccupancy * 0.5) + random(-5, 8);
    // Clamp between 0 and 100
    pollution = Math.min(100, Math.max(0, pollution));

    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      occupancy: currentOccupancy,
      waterQuality: currentWaterQuality,
      airQuality: currentAirQuality,
      temperature: currentTemp,
      pollutionLevel: Math.floor(pollution)
    });
  }
  return data;
};

export const getBeachData = (beachId: string): BeachData | null => {
  const beach = BEACHES.find(b => b.id === beachId);
  if (!beach) return null;

  const history = generateHistoricalData(7);
  const currentStats = history[history.length - 1];

  return {
    ...beach,
    history,
    currentStats
  };
};

export const getAllBeachesData = (): BeachData[] => {
  return BEACHES.map(beach => {
    const history = generateHistoricalData(7);
    return {
      ...beach,
      history,
      currentStats: history[history.length - 1]
    };
  });
};