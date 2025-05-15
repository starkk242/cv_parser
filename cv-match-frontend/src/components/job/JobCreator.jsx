import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  VStack,
  HStack,
  Heading,
  Text,
  useToast,
  Divider,
  SimpleGrid,
  Icon,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiSave, FiUpload, FiBriefcase, FiInfo } from 'react-icons/fi';
import FileUpload from '../common/FileUpload';
import { createJob } from '../../api/jobs';

const JobCreator = ({ onJobCreated }) => {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');
  const [requiredSkills, setRequiredSkills] = useState('');
  const [preferredSkills, setPreferredSkills] = useState('');
  const [educationRequirements, setEducationRequirements] = useState('');
  const [experienceRequirements, setExperienceRequirements] = useState('');
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  
  const handleFileChange = (files) => {
    setFile(files[0] || null);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title) {
      toast({
        title: 'Title required',
        description: 'Please enter a job title.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    if (!description && !file) {
      toast({
        title: 'Description required',
        description: 'Please either enter a job description or upload a file.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    const jobData = {
      title,
      company,
      description,
      required_skills: requiredSkills,
      preferred_skills: preferredSkills,
      education_requirements: educationRequirements,
      experience_requirements: experienceRequirements,
      file,
    };
    
    setIsLoading(true);
    try {
      const createdJob = await createJob(jobData);
      toast({
        title: 'Job created',
        description: 'Job description has been successfully created.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Reset form
      setTitle('');
      setCompany('');
      setDescription('');
      setRequiredSkills('');
      setPreferredSkills('');
      setEducationRequirements('');
      setExperienceRequirements('');
      setFile(null);
      
      // Notify parent component
      if (onJobCreated) onJobCreated(createdJob);
    } catch (error) {
      console.error('Error creating job:', error);
      toast({
        title: 'Error',
        description: error.detail || 'Failed to create job description.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card bg={cardBg} shadow="md" borderRadius="lg">
      <CardHeader>
        <Heading size="md">
          <Icon as={FiBriefcase} mr={2} />
          Create New Job Description
        </Heading>
        <Text mt={2} color="gray.600">
          Enter job details manually or upload a file with the job description.
        </Text>
      </CardHeader>
      <Divider />
      <CardBody>
        <form onSubmit={handleSubmit}>
          <VStack spacing={6} align="stretch">
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <FormControl isRequired>
                <FormLabel>Job Title</FormLabel>
                <Input 
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Senior Software Engineer"
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>Company</FormLabel>
                <Input 
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. Tech Solutions Inc."
                />
              </FormControl>
            </SimpleGrid>
            
            <FormControl>
              <FormLabel>Job Description</FormLabel>
              <Textarea 
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter detailed job description..."
                rows={6}
              />
            </FormControl>
            
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <FormControl>
                <FormLabel>Required Skills</FormLabel>
                <Textarea 
                  value={requiredSkills}
                  onChange={(e) => setRequiredSkills(e.target.value)}
                  placeholder="e.g. JavaScript, React, Node.js"
                  rows={3}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Separate skills with commas
                </Text>
              </FormControl>
              
              <FormControl>
                <FormLabel>Preferred Skills</FormLabel>
                <Textarea 
                  value={preferredSkills}
                  onChange={(e) => setPreferredSkills(e.target.value)}
                  placeholder="e.g. TypeScript, GraphQL, AWS"
                  rows={3}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Separate skills with commas
                </Text>
              </FormControl>
            </SimpleGrid>
            
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <FormControl>
                <FormLabel>Education Requirements</FormLabel>
                <Textarea 
                  value={educationRequirements}
                  onChange={(e) => setEducationRequirements(e.target.value)}
                  placeholder="e.g. Bachelor's in Computer Science"
                  rows={3}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Separate requirements with commas
                </Text>
              </FormControl>
              
              <FormControl>
                <FormLabel>Experience Requirements</FormLabel>
                <Textarea 
                  value={experienceRequirements}
                  onChange={(e) => setExperienceRequirements(e.target.value)}
                  placeholder="e.g. 3+ years of frontend development"
                  rows={3}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Separate requirements with commas
                </Text>
              </FormControl>
            </SimpleGrid>
            
            <Box>
              <FormLabel>Or Upload a Job Description File</FormLabel>
              <FileUpload 
                accept=".pdf,.docx,.txt" 
                multiple={false}
                onChange={handleFileChange}
                maxSize={5}
                maxFiles={1}
                height="150px"
              />
            </Box>
          </VStack>
        </form>
      </CardBody>
      <Divider />
      <CardFooter>
        <Button
          leftIcon={<FiSave />}
          colorScheme="blue"
          isLoading={isLoading}
          loadingText="Creating..."
          onClick={handleSubmit}
          size="lg"
        >
          Create Job
        </Button>
      </CardFooter>
    </Card>
  );
};

export default JobCreator;