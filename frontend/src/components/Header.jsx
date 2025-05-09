import React from 'react';

export function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-12">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">Resume Parser</h1>
        <p className="text-xl md:text-2xl max-w-3xl mx-auto">
          Upload multiple resumes, get structured data instantly
        </p>
      </div>
    </header>
  );
}
