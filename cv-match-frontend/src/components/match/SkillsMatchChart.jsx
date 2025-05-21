import React from 'react';
import { Box, useColorModeValue } from '@chakra-ui/react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const SkillsMatchChart = ({ match, height = 200 }) => {
  const textColor = useColorModeValue('rgba(0, 0, 0, 0.8)', 'rgba(255, 255, 255, 0.8)');
  
  // Calculate percentages
  // const matchedSkillsCount = match.matched_skills.length;
  // const missingSkillsCount = match.missing_skills.length;

  const matchedSkillsCount = match.skills_score;
  const missingSkillsCount = 100 - match.skills_score;
  const totalSkills = matchedSkillsCount + missingSkillsCount;
  
  if (totalSkills === 0) {
    return (
      <Box height={height} display="flex" alignItems="center" justifyContent="center">
        No skills data available for chart
      </Box>
    );
  }
  
  const data = {
    labels: ['Matched Skills', 'Missing Skills'],
    datasets: [
      {
        data: [matchedSkillsCount, missingSkillsCount],
        backgroundColor: [
          'rgba(72, 187, 120, 0.7)',  // green.500 with opacity
          'rgba(245, 101, 101, 0.7)',  // red.500 with opacity
        ],
        borderColor: [
          'rgba(72, 187, 120, 1)',  // green.500
          'rgba(245, 101, 101, 1)',  // red.500
        ],
        borderWidth: 1,
      },
    ],
  };
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: textColor,
          font: {
            size: 12
          },
          generateLabels: (chart) => {
            const datasets = chart.data.datasets;
            const labels = chart.data.labels;
            
            return labels.map((label, i) => {
              const meta = chart.getDatasetMeta(0);
              const value = datasets[0].data[i];
              const percentage = ((value / totalSkills) * 100).toFixed(1);
              
              return {
                text: `${label} (${value}, ${percentage}%)`,
                fillStyle: datasets[0].backgroundColor[i],
                strokeStyle: datasets[0].borderColor[i],
                lineWidth: 1,
                hidden: false,
                index: i
              };
            });
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.raw;
            const percentage = ((value / totalSkills) * 100).toFixed(1);
            // return `${context.label}: ${value} (${percentage}%)`;
            return `${context.label}`;
          }
        }
      }
    },
  };
  
  return (
    <Box height={height}>
      <Pie data={data} options={options} />
    </Box>
  );
};

export default SkillsMatchChart;