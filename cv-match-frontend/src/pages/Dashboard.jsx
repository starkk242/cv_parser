import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  SimpleGrid,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardBody,
  HStack,
  VStack,
  Icon,
  Button,
  Flex,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import {
  FiFileText,
  FiBriefcase,
  FiSearch,
  FiUsers,
  FiArrowRight,
  FiPieChart,
  FiActivity
} from 'react-icons/fi';
import { getJobs } from '../api/jobs';

const StatCard = ({ title, value, icon, color, helpText }) => {
  return (
    <Card shadow="sm" borderRadius="lg">
      <CardBody>
        <Stat>
          <HStack spacing={4}>
            <Box
              p={2}
              borderRadius="md"
              bg={`${color}.100`}
              color={`${color}.700`}
            >
              <Icon as={icon} boxSize={6} />
            </Box>
            <Box>
              <StatLabel>{title}</StatLabel>
              <StatNumber fontSize="3xl">{value}</StatNumber>
              {helpText && <StatHelpText>{helpText}</StatHelpText>}
            </Box>
          </HStack>
        </Stat>
      </CardBody>
    </Card>
  );
};

const FeatureCard = ({ title, description, icon, linkTo, linkText, color }) => {
  return (
    <Card 
      shadow="sm" 
      borderRadius="lg" 
      height="100%"
      borderTop="4px solid"
      borderColor={`${color}.500`}
      transition="all 0.2s"
      _hover={{ transform: "translateY(-5px)", shadow: "md" }}
    >
      <CardBody>
        <VStack spacing={4} align="start">
          <Box
            p={2}
            borderRadius="md"
            bg={`${color}.100`}
            color={`${color}.700`}
          >
            <Icon as={icon} boxSize={6} />
          </Box>
          <Heading size="md">{title}</Heading>
          <Text color="gray.600">{description}</Text>
          <Divider />
          <Button
            as={RouterLink}
            to={linkTo}
            rightIcon={<FiArrowRight />}
            variant="ghost"
            colorScheme={color}
            alignSelf="flex-end"
            mt="auto"
          >
            {linkText}
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
};

const Dashboard = () => {
  const [jobCount, setJobCount] = useState(0);
  
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const jobs = await getJobs();
        setJobCount(jobs.length);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      }
    };
    
    fetchJobs();
  }, []);
  
  return (
    <Box>
      <Box mb={8}>
        <Heading mb={2}>Welcome to CV-Match</Heading>
        <Text color="gray.600">
          Your all-in-one solution for CV parsing, job matching, and candidate evaluation
        </Text>
      </Box>
      
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={10}>
        <StatCard
          title="Job Descriptions"
          value={jobCount}
          icon={FiBriefcase}
          color="blue"
          helpText="Active job descriptions"
        />
        <StatCard
          title="Recent Matches"
          value="24"
          icon={FiSearch}
          color="green"
          helpText="Last 7 days"
        />
        <StatCard
          title="CVs Processed"
          value="143"
          icon={FiUsers}
          color="purple"
          helpText="Total CVs parsed"
        />
      </SimpleGrid>
      
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
        <FeatureCard
          title="Parse CVs"
          description="Upload and parse CV/Resume files to extract key information including contact details, skills, education, and experience."
          icon={FiFileText}
          linkTo="/cv-parser"
          linkText="Go to CV Parser"
          color="blue"
        />
        <FeatureCard
          title="Manage Jobs"
          description="Create and manage job descriptions with detailed requirements including skills, education, and experience."
          icon={FiBriefcase}
          linkTo="/jobs"
          linkText="Manage Jobs"
          color="purple"
        />
        <FeatureCard
          title="Match CVs to Jobs"
          description="Match uploaded CVs against job descriptions to find the best candidates with comprehensive scoring and analysis."
          icon={FiSearch}
          linkTo="/match"
          linkText="Start Matching"
          color="green"
        />
      </SimpleGrid>
      
      <Card mt={10} shadow="sm" borderRadius="lg">
        <CardBody>
          <VStack spacing={4} align="start">
            <Heading size="md" display="flex" alignItems="center">
              <Icon as={FiActivity} mr={2} />
              Getting Started
            </Heading>
            <Divider />
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} width="100%">
              <Box bg={useColorModeValue('gray.50', 'gray.700')} p={4} borderRadius="md">
                <Text fontWeight="bold" mb={2}>1. Create Job Descriptions</Text>
                <Text fontSize="sm">
                  Start by creating job descriptions with detailed requirements, skills, and qualifications.
                </Text>
              </Box>
              <Box bg={useColorModeValue('gray.50', 'gray.700')} p={4} borderRadius="md">
                <Text fontWeight="bold" mb={2}>2. Parse CVs</Text>
                <Text fontSize="sm">
                  Upload and parse CV/Resume files to extract structured information.
                </Text>
              </Box>
              <Box bg={useColorModeValue('gray.50', 'gray.700')} p={4} borderRadius="md">
                <Text fontWeight="bold" mb={2}>3. Match and Analyze</Text>
                <Text fontSize="sm">
                  Match CVs against job descriptions to identify the most suitable candidates.
                </Text>
              </Box>
            </SimpleGrid>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  );
};

export default Dashboard;