import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  Select,
  FormControl,
  FormLabel,
  Stack,
  useToast,
  Icon,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Divider,
  useColorModeValue,
  Flex,
  Checkbox,
  CheckboxGroup,
} from '@chakra-ui/react';
import { FiFileText, FiSearch, FiDownload } from 'react-icons/fi';
import FileUpload from '../common/FileUpload';
import { getJobs } from '../../api/jobs';
import { matchResumes, exportMatchResults } from '../../api/matching';

const MatchingForm = ({ onMatchResults }) => {
  const [files, setFiles] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isLoadingJobs, setIsLoadingJobs] = useState(false);
  
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  
  useEffect(() => {
    loadJobs();
  }, []);
  
  const loadJobs = async () => {
    setIsLoadingJobs(true);
    try {
      const jobsData = await getJobs();
      setJobs(jobsData);
      if (jobsData.length > 0) {
        setSelectedJobId(jobsData[0].id);
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
      toast({
        title: 'Error loading jobs',
        description: error.detail || 'Could not load job descriptions.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoadingJobs(false);
    }
  };
  
  const handleMatch = async () => {
    if (!selectedJobId) {
      toast({
        title: 'No job selected',
        description: 'Please select a job description to match against.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    if (files.length === 0) {
      toast({
        title: 'No files selected',
        description: 'Please select at least one CV to match.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsLoading(true);
    try {
      const results = await matchResumes(selectedJobId, files);
      if (onMatchResults) onMatchResults(results, getSelectedJobTitle());
      
      toast({
        title: 'Matching complete',
        description: `${files.length} CV(s) matched against the selected job.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Matching error:', error);
      toast({
        title: 'Matching failed',
        description: error.detail || 'An error occurred while matching the CVs.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleExportExcel = async () => {
    if (!selectedJobId) {
      toast({
        title: 'No job selected',
        description: 'Please select a job description to match against.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    if (files.length === 0) {
      toast({
        title: 'No files selected',
        description: 'Please select at least one CV to match.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsExporting(true);
    try {
      await exportMatchResults(selectedJobId, files);
      toast({
        title: 'Excel exported',
        description: 'Match results have been exported to Excel.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: 'Export failed',
        description: error.detail || 'An error occurred while exporting the results.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsExporting(false);
    }
  };
  
  const getSelectedJobTitle = () => {
    const job = jobs.find(j => j.id === selectedJobId);
    return job ? job.title : 'Selected Job';
  };
  
  return (
    <Card bg={cardBg} shadow="md" borderRadius="lg">
      <CardHeader>
        <Heading size="md">
          <Icon as={FiSearch} mr={2} />
          Match CVs to Job Description
        </Heading>
        <Text mt={2} color="gray.600">
          Select a job description and upload CV files to find the best matches.
        </Text>
      </CardHeader>
      
      <Divider />
      
      <CardBody>
        <VStack spacing={6} align="stretch">
          <FormControl isRequired>
            <FormLabel>Select Job Description</FormLabel>
            <Select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              placeholder="Select a job description"
              isDisabled={isLoadingJobs || jobs.length === 0}
            >
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} {job.company ? `- ${job.company}` : ''}
                </option>
              ))}
            </Select>
            {isLoadingJobs && (
              <Text fontSize="sm" color="gray.500" mt={1}>
                Loading job descriptions...
              </Text>
            )}
            {!isLoadingJobs && jobs.length === 0 && (
              <Text fontSize="sm" color="red.500" mt={1}>
                No job descriptions available. Please create a job description first.
              </Text>
            )}
          </FormControl>
          
          <FormControl isRequired>
            <FormLabel>Upload CVs to Match</FormLabel>
            <FileUpload 
              accept=".pdf,.docx,.txt" 
              multiple={true} 
              onChange={setFiles}
              maxSize={10}
              maxFiles={50}
            />
          </FormControl>
        </VStack>
      </CardBody>
      
      <Divider />
      
      <CardFooter>
        <Stack direction={{ base: "column", md: "row" }} spacing={4} width="100%">
          <Button
            leftIcon={<FiSearch />}
            colorScheme="blue"
            isLoading={isLoading}
            loadingText="Matching..."
            onClick={handleMatch}
            flex={{ md: 1 }}
            size="lg"
            isDisabled={files.length === 0 || !selectedJobId || isExporting}
          >
            Match CVs
          </Button>
          
          <Button
            leftIcon={<FiDownload />}
            colorScheme="green"
            variant="outline"
            isLoading={isExporting}
            loadingText="Exporting..."
            onClick={handleExportExcel}
            flex={{ md: 1 }}
            size="lg"
            isDisabled={files.length === 0 || !selectedJobId || isLoading}
          >
            Export to Excel
          </Button>
        </Stack>
      </CardFooter>
    </Card>
  );
};

export default MatchingForm;