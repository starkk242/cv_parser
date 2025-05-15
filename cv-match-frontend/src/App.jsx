import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import MainLayout from './layouts/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import CVParser from './pages/CVParser';
import JobsManager from './pages/JobsManager';
import MatchResults from './pages/MatchResults';

// Custom theme
const theme = extendTheme({
  fonts: {
    heading: `'Inter', sans-serif`,
    body: `'Inter', sans-serif`,
  },
  colors: {
    brand: {
      50: '#e6f7ff',
      100: '#b3e0ff',
      200: '#80c9ff',
      300: '#4db2ff',
      400: '#1a9cff',
      500: '#0084e6',
      600: '#0068b3',
      700: '#004d80',
      800: '#00334d',
      900: '#001a1a',
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '500',
      },
    },
    Heading: {
      baseStyle: {
        fontWeight: '600',
      },
    },
  },
});

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cv-parser" element={<CVParser />} />
            <Route path="/jobs" element={<JobsManager />} />
            <Route path="/match" element={<MatchResults />} />
          </Routes>
        </MainLayout>
      </Router>
    </ChakraProvider>
  );
}

export default App;