import React, { useState, useRef } from 'react';
import { FileUploader } from './components/FileUploader';
import { ResultsTable } from './components/ResultsTable';
import { LoadingState } from './components/LoadingState';
import { ErrorAlert } from './components/ErrorAlert';
import { SuccessAlert } from './components/SuccessAlert';
import { Header } from './components/Header';

function App() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (selectedFiles) => {
    // Convert FileList to Array
    const filesArray = Array.from(selectedFiles);
    
    // Filter for allowed extensions
    const allowedExtensions = ['.pdf', '.docx'];
    const validFiles = filesArray.filter(file => {
      const extension = '.' + file.name.split('.').pop().toLowerCase();
      return allowedExtensions.includes(extension);
    });
    
    if (validFiles.length !== filesArray.length) {
      setError("Some files were removed. Only PDF and DOCX files are accepted.");
    }
    
    setFiles(validFiles);
  };

  const resetForm = () => {
    setFiles([]);
    setResults([]);
    setError(null);
    setSuccess(null);
    setDownloadUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (format = 'json') => {
    if (files.length === 0) {
      setError("Please select at least one resume file.");
      return;
    }

    setError(null);
    setUploading(true);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      
      formData.append('format', format);
      
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload files');
      }
      
      if (format === 'excel') {
        // For Excel format, we get a file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        setDownloadUrl(url);
        
        // Automatically trigger download
        const a = document.createElement('a');
        a.href = url;
        a.download = `parsed_resumes_${new Date().toISOString().slice(0,10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        setSuccess(`Successfully parsed ${files.length} resume(s) and downloaded Excel file.`);
      } else {
        // For JSON format, we display the results
        const data = await response.json();
        setResults(data);
        setSuccess(`Successfully parsed ${data.length} resume(s).`);
      }
    } catch (err) {
      setError(err.message || 'An error occurred while processing the files.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Upload Resumes</h2>
          
          {error && <ErrorAlert message={error} onClose={() => setError(null)} />}
          {success && <SuccessAlert message={success} onClose={() => setSuccess(null)} />}
          
          <FileUploader 
            files={files}
            onFileChange={handleFileChange}
            fileInputRef={fileInputRef}
          />
          
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => handleSubmit('json')}
              disabled={uploading || files.length === 0}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
            >
              Parse Resumes
            </button>
            
            <button
              onClick={() => handleSubmit('excel')}
              disabled={uploading || files.length === 0}
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
            >
              Download as Excel
            </button>
            
            <button
              onClick={resetForm}
              className="border border-gray-300 hover:bg-gray-100 text-gray-700 font-medium py-2 px-4 rounded"
            >
              Reset
            </button>
          </div>
        </div>
        
        {uploading && <LoadingState />}
        
        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Parsing Results</h2>
            <ResultsTable results={results} />
          </div>
        )}
      </main>
      
      <footer className="bg-gray-800 text-white py-6">
        <div className="container mx-auto px-4 text-center">
          <p>Resume Parser App © {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  );
}

export default App;