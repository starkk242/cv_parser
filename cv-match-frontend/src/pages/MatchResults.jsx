import React, { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Icon,
  Divider,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FiHome, FiSearch } from 'react-icons/fi';
import MatchingForm from '../components/match/MatchingForm';
import MatchResults from '../components/match/MatchResults';

const MatchingPage = () => {
  const [results, setResults] = useState([]);
  const [jobTitle, setJobTitle] = useState('');
  // Add state to control active tab
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  
  const handleMatchResults = (data, title) => {
    setResults(data);
    setJobTitle(title);
    
    // Switch to results tab using state instead of DOM manipulation
    setTimeout(() => {
      setActiveTabIndex(1);
    }, 100);
  };
  
  return (
    <Box>
      <Breadcrumb mb={6}>
        <BreadcrumbItem>
          <BreadcrumbLink as={RouterLink} to="/">
            <Icon as={FiHome} mr={1} />
            Home
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>
          <BreadcrumbLink>
            <Icon as={FiSearch} mr={1} />
            Match CVs
          </BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>
      
      <Box mb={8}>
        <Heading mb={2}>CV-Job Matching</Heading>
        <Text color="gray.600">
          Match CVs against job descriptions to find the best candidates with detailed scoring and analysis.
        </Text>
      </Box>
      
      <Tabs 
        variant="soft-rounded" 
        colorScheme="blue" 
        index={activeTabIndex} 
        onChange={setActiveTabIndex}
      >
        <TabList mb={6}>
          <Tab>Match CVs</Tab>
          <Tab isDisabled={results.length === 0}>
            Results {results.length > 0 && `(${results.length})`}
          </Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel p={0}>
            <MatchingForm onMatchResults={handleMatchResults} />
          </TabPanel>
          
          <TabPanel p={0}>
            <MatchResults results={results} jobTitle={jobTitle} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default MatchingPage;