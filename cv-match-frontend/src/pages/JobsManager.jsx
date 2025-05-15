import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  Button,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Skeleton,
  Icon,
  useToast,
  useDisclosure
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FiHome, FiBriefcase, FiPlus } from 'react-icons/fi';
import JobCreator from '../components/job/JobCreator';
import JobCard from '../components/job/JobCard';
import JobDetails from '../components/job/JobDetails';
import { getJobs } from '../api/jobs';

const JobsManager = () => {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const toast = useToast();
  
  useEffect(() => {
    fetchJobs();
  }, []);
  
  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      const jobsData = await getJobs();
      setJobs(jobsData);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      toast({
        title: 'Error',
        description: 'Failed to load job descriptions',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleJobCreated = (newJob) => {
    setJobs([...jobs, newJob]);
    toast({
      title: 'Job Created',
      description: 'The job description has been successfully created',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  const handleViewDetails = (job) => {
    setSelectedJob(job);
  };
  
  const handleBackToJobs = () => {
    setSelectedJob(null);
  };
  
  // If a job is selected, show its details
  if (selectedJob) {
    return (
      <Box>
        <Breadcrumb mb={6}>
          <BreadcrumbItem>
            <BreadcrumbLink as={RouterLink} to="/">
              <Icon as={FiHome} mr={1} />
              Home
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem>
            <BreadcrumbLink onClick={handleBackToJobs}>
              <Icon as={FiBriefcase} mr={1} />
              Jobs
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink>{selectedJob.title}</BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>
        
        <JobDetails job={selectedJob} onBack={handleBackToJobs} />
      </Box>
    );
  }
  
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
            <Icon as={FiBriefcase} mr={1} />
            Jobs
          </BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>
      
      <Box mb={8}>
        <Heading mb={2}>Job Descriptions Manager</Heading>
        <Text color="gray.600">
          Create, manage, and organize job descriptions for matching with candidate CVs.
        </Text>
      </Box>
      
      <Tabs variant="soft-rounded" colorScheme="blue">
        <TabList mb={6}>
          <Tab>Job Listings ({jobs.length})</Tab>
          <Tab id="create-job-tab">Create New Job</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel p={0}>
            {isLoading ? (
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} height="200px" borderRadius="lg" />
                ))}
              </SimpleGrid>
            ) : jobs.length === 0 ? (
              <Box textAlign="center" py={10}>
                <Heading size="md" mb={3}>No Job Descriptions Found</Heading>
                <Text mb={6}>Get started by creating your first job description.</Text>
                <Button
                  leftIcon={<FiPlus />}
                  colorScheme="blue"
                  onClick={() => document.getElementById('create-job-tab').click()}
                >
                  Create Job Description
                </Button>
              </Box>
            ) : (
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onViewDetails={() => handleViewDetails(job)}
                  />
                ))}
              </SimpleGrid>
            )}
          </TabPanel>
          
          <TabPanel p={0}>
            <JobCreator onJobCreated={handleJobCreated} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default JobsManager;