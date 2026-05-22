import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  submitAnalysis: async ({ companyName, industry, depth, jobType }) => {
    const endpoint = jobType === 'marketing' ? '/api/marketing' : (jobType === 'future' ? '/api/future' : '/api/analyze');
    const response = await client.post(endpoint, {
      company_name: companyName,
      industry: industry,
      depth,
    });
    return response.data; // { job_id, status }
  },
  
  getJobStatus: async (jobId) => {
    const response = await client.get(`/api/status/${jobId}`);
    return response.data; // { job_id, company_name, industry, status, progress, logs, error_log }
  },
  
  getReport: async (jobId) => {
    const response = await client.get(`/api/report/${jobId}`);
    return response.data; // { metadata, target_company, competitor_data, competitor_profiles, swot, sentiment, ads_analysis, market_opportunity, recommendations }
  },
  
  getPdfDownloadUrl: (jobId) => {
    return `${API_BASE_URL}/api/export/pdf/${jobId}`;
  }
};

export default client;
