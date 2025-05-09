import React from 'react';
import { FileText, X } from 'lucide-react';

export function FileUploader({ files, onFileChange, fileInputRef }) {
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileChange(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileChange(e.target.files);
    }
  };

  const removeFile = (indexToRemove) => {
    const newFiles = files.filter((_, index) => index !== indexToRemove);
    const dataTransfer = new DataTransfer();
    
    newFiles.forEach(file => {
      dataTransfer.items.add(file);
    });
    
    if (fileInputRef.current) {
      fileInputRef.current.files = dataTransfer.files;
    }
    
    onFileChange(dataTransfer.files);
  };

  return (
    <div className="space-y-4">
      <div 
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInputChange}
          accept=".pdf,.docx"
          multiple
          className="hidden"
        />
        
        <FileText className="mx-auto h-12 w-12 text-gray-400" />
        
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-900">
            Drop resumes here or click to upload
          </p>
          <p className="text-xs text-gray-500 mt-1">
            PDF, DOCX (Max 10MB per file)
          </p>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            {files.length} file(s) selected
          </h3>
          
          <ul className="space-y-2">
            {files.map((file, index) => (
              <li 
                key={`${file.name}-${index}`} 
                className="flex items-center justify-between bg-gray-50 rounded px-3 py-2"
              >
                <div className="flex items-center space-x-2 truncate">
                  <FileText className="h-5 w-5 text-blue-500" />
                  <span className="text-sm text-gray-700 truncate">
                    {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                  </span>
                </div>
                
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}