import React from 'react';

export function LoadingState() {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-solid border-blue-600 border-r-transparent align-middle"></div>
        <div className="mt-4 text-gray-700">
          <p className="font-medium">Processing your resume files...</p>
          <p className="text-sm mt-1">This may take a few moments depending on the number and size of files.</p>
        </div>
      </div>
    </div>
  );
}