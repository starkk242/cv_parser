import api from './index';

export const createJob = async (jobData) => {
  const formData = new FormData();
  
  // Add text fields
  formData.append('title', jobData.title);
  if (jobData.company) formData.append('company', jobData.company);
  if (jobData.description) formData.append('description', jobData.description);
  if (jobData.required_skills) formData.append('required_skills', jobData.required_skills);
  if (jobData.preferred_skills) formData.append('preferred_skills', jobData.preferred_skills);
  if (jobData.education_requirements) formData.append('education_requirements', jobData.education_requirements);
  if (jobData.experience_requirements) formData.append('experience_requirements', jobData.experience_requirements);
  
  // Add file if provided
  if (jobData.file) formData.append('file', jobData.file);
  
  try {
    const response = await api.post('/job', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getJobs = async () => {
  try {
    const response = await api.get('/jobs');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getJob = async (jobId) => {
  try {
    const response = await api.get(`/job/${jobId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};