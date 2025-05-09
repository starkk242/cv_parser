import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export function ResultsTable({ results }) {
  const [expanded, setExpanded] = useState({});

  const toggleExpand = (index) => {
    setExpanded({
      ...expanded,
      [index]: !expanded[index]
    });
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              File Name
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Phone
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {results.map((result, index) => (
            <React.Fragment key={index}>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {result.file_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {result.name || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {result.email || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {result.phone || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button 
                    onClick={() => toggleExpand(index)}
                    className="text-blue-600 hover:text-blue-900 flex items-center"
                  >
                    {expanded[index] ? (
                      <>
                        <span>Hide Details</span>
                        <ChevronUp className="h-4 w-4 ml-1" />
                      </>
                    ) : (
                      <>
                        <span>Show Details</span>
                        <ChevronDown className="h-4 w-4 ml-1" />
                      </>
                    )}
                  </button>
                </td>
              </tr>
              
              {expanded[index] && (
                <tr>
                  <td colSpan="5" className="px-6 py-4 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Skills</h4>
                        <div className="flex flex-wrap gap-2 mb-4">
                          {result.skills && result.skills.length > 0 ? (
                            result.skills.map((skill, i) => (
                              <span key={i} className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                                {skill}
                              </span>
                            ))
                          ) : (
                            <span className="text-gray-500 text-sm">No skills extracted</span>
                          )}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Education</h4>
                        {result.education && result.education.length > 0 ? (
                          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                            {result.education.map((edu, i) => (
                              <li key={i}>{edu}</li>
                            ))}
                          </ul>
                        ) : (
                          <span className="text-gray-500 text-sm">No education extracted</span>
                        )}
                      </div>
                      
                      <div className="md:col-span-2">
                        <h4 className="font-medium text-gray-900 mb-2">Experience</h4>
                        {result.experience && result.experience.length > 0 ? (
                          <ul className="list-disc list-inside text-sm text-gray-700 space-y-2">
                            {result.experience.map((exp, i) => (
                              <li key={i}>{exp.description}</li>
                            ))}
                          </ul>
                        ) : (
                          <span className="text-gray-500 text-sm">No experience extracted</span>
                        )}
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}