import React from 'react';
import {
  Box,
  Heading,
  Text,
  Badge,
  HStack,
  VStack,
  Divider,
  SimpleGrid,
  Icon,
  Button,
  List,
  ListItem,
  ListIcon,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  useColorModeValue,
  Flex,
  Wrap,
  WrapItem,
  Tag,
} from '@chakra-ui/react';
import {
  FiBriefcase,
  FiUsers,
  FiCalendar,
  FiCheckCircle,
  FiCode,
  FiBook,
  FiClock,
  FiChevronLeft
} from 'react-icons/fi';
import { format, parseISO } from 'date-fns';

const JobDetails = ({ job, onBack }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const sectionBg = useColorModeValue('gray.50', 'gray.700');
  
  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'MMMM d, yyyy');
    } catch (error) {
      return dateString;
    }
  };
  
  if (!job) return null;
  
  return (
    <Card bg={cardBg} shadow="md" borderRadius="lg">
      <CardHeader>
        <Button
          leftIcon={<FiChevronLeft />}
          variant="ghost"
          mb={4}
          onClick={onBack}
        >
          Back to Jobs
        </Button>
        
        <VStack align="start" spacing={2} mb={4}>
          <HStack spacing={2}>
            <Icon as={FiBriefcase} color="blue.500" boxSize={5} />
            <Heading size="lg">{job.title}</Heading>
          </HStack>
          
          {job.company && (
            <HStack spacing={2}>
              <Icon as={FiUsers} color="gray.500" />
              <Text fontSize="lg" color="gray.600">{job.company}</Text>
            </HStack>
          )}
          
          <HStack spacing={2}>
            <Icon as={FiCalendar} color="gray.500" />
            <Text fontSize="sm" color="gray.500">
              Posted on {formatDate(job.created_date)}
            </Text>
          </HStack>
        </VStack>
        
        <Divider />
      </CardHeader>
      
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* Job Description */}
          <Box>
            <Heading size="md" mb={4}>Description</Heading>
            <Box p={4} bg={sectionBg} borderRadius="md" whiteSpace="pre-line">
              <Text>{job.description}</Text>
            </Box>
          </Box>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {/* Required Skills */}
            <Box>
              <Heading size="sm" display="flex" alignItems="center" mb={4}>
                <Icon as={FiCode} mr={2} color="blue.500" />
                Required Skills
              </Heading>
              
              {job.required_skills && job.required_skills.length > 0 ? (
                <Wrap spacing={2}>
                  {job.required_skills.map((skill, index) => (
                    <WrapItem key={index}>
                      <Tag colorScheme="blue" size="md" borderRadius="full" py={1} px={3}>
                        {skill}
                      </Tag>
                    </WrapItem>
                  ))}
                </Wrap>
              ) : (
                <Text color="gray.500">No required skills specified</Text>
              )}
            </Box>
            
            {/* Preferred Skills */}
            <Box>
              <Heading size="sm" display="flex" alignItems="center" mb={4}>
                <Icon as={FiCode} mr={2} color="green.500" />
                Preferred Skills
              </Heading>
              
              {job.preferred_skills && job.preferred_skills.length > 0 ? (
                <Wrap spacing={2}>
                  {job.preferred_skills.map((skill, index) => (
                    <WrapItem key={index}>
                      <Tag colorScheme="green" variant="outline" size="md" borderRadius="full" py={1} px={3}>
                        {skill}
                      </Tag>
                    </WrapItem>
                  ))}
                </Wrap>
              ) : (
                <Text color="gray.500">No preferred skills specified</Text>
              )}
            </Box>
          </SimpleGrid>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {/* Education Requirements */}
            <Box>
              <Heading size="sm" display="flex" alignItems="center" mb={4}>
                <Icon as={FiBook} mr={2} color="purple.500" />
                Education Requirements
              </Heading>
              
              {job.education_requirements && job.education_requirements.length > 0 ? (
                <List spacing={2}>
                  {job.education_requirements.map((edu, index) => (
                    <ListItem key={index} display="flex" alignItems="flex-start">
                      <ListIcon as={FiCheckCircle} color="purple.500" mt={1} />
                      <Text>{edu}</Text>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Text color="gray.500">No education requirements specified</Text>
              )}
            </Box>
            
            {/* Experience Requirements */}
            <Box>
              <Heading size="sm" display="flex" alignItems="center" mb={4}>
                <Icon as={FiClock} mr={2} color="orange.500" />
                Experience Requirements
              </Heading>
              
              {job.experience_requirements && job.experience_requirements.length > 0 ? (
                <List spacing={2}>
                  {job.experience_requirements.map((exp, index) => (
                    <ListItem key={index} display="flex" alignItems="flex-start">
                      <ListIcon as={FiCheckCircle} color="orange.500" mt={1} />
                      <Text>{exp}</Text>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Text color="gray.500">No experience requirements specified</Text>
              )}
            </Box>
          </SimpleGrid>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default JobDetails;