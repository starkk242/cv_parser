import React from 'react';
import { XCircle, X, CheckCircle } from 'lucide-react';

export function ErrorAlert({ message, onClose }) {
  return (
    <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4 rounded">
      <div className="flex">
        <div className="flex-shrink-0">
          <XCircle className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3 flex-1">
          <div className="text-sm text-red-700">
            {message}
          </div>
        </div>
        <div className="pl-3">
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={onClose}
                className="inline-flex rounded-md p-1.5 text-red-500 hover:bg-red-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SuccessAlert({ message, onClose }) {
  return (
    <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-4 rounded">
      <div className="flex">
        <div className="flex-shrink-0">
          <CheckCircle className="h-5 w-5 text-green-400" />
        </div>
        <div className="ml-3 flex-1">
          <div className="text-sm text-green-700">
            {message}
          </div>
        </div>
        <div className="pl-3">
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={onClose}
                className="inline-flex rounded-md p-1.5 text-green-500 hover:bg-green-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}