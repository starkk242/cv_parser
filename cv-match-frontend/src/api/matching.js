import api from './index';

export const matchResumes = async (jobId, files) => {
  const formData = new FormData();
  formData.append('job_id', jobId);
  files.forEach(file => {
    formData.append('files', file);
  });
  
  try {
    const response = await api.post('/match', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const batchMatchResumes = async (jobIds, files) => {
  const formData = new FormData();
  formData.append('job_ids', jobIds.join(','));
  files.forEach(file => {
    formData.append('files', file);
  });
  
  try {
    const response = await api.post('/batch-match', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const exportMatchResults = async (jobId, files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  try {
    const response = await api.post(`/export-matches/${jobId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `job_matches_${jobId}_${new Date().toISOString().slice(0, 10)}.xlsx`);
    document.body.appendChild(link);
    link.click();
    
    return true;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};