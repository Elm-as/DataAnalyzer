// Configuration du backend
const BACKEND_URL = 'http://localhost:5000';

export const api = {

  // Analyses de base (maintenant aussi en Python pour plus de précision)
  basicAnalysis: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/basic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  // Analyses avancées (backend Python)
  regression: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/regression`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  classification: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/classification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  discriminant: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/discriminant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  neuralNetworks: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/neural-networks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },

  // Détection et conversion automatique des colonnes booléennes
  detectBooleans: async (data: any) => {
    const response = await fetch(`${BACKEND_URL}/detect-booleans`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    });
    return response.json();
  },
  
  timeSeries: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/time-series`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  clusteringAdvanced: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/clustering-advanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  dataCleaning: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/clean/data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  advancedStats: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/advanced-stats`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  symptomMatching: async (data: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/analyze/symptom-matching`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, config })
    });
    return response.json();
  },
  
  generateReport: async (results: any, config: any) => {
    const response = await fetch(`${BACKEND_URL}/report/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ results, config })
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate report');
    }
    
    // Get the PDF as a blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rapport_analyse_${new Date().toISOString().slice(0,10)}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    return { success: true, message: 'Rapport PDF téléchargé' };
  },
  
  healthCheck: async () => {
    const response = await fetch(`${BACKEND_URL}/health`);
    return response.json();
  }
};
