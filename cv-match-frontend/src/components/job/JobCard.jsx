import React from 'react';
import {
  Box,
  Heading,
  Text,
  Badge,
  HStack,
  VStack,
  Button,
  Icon,
  useColorModeValue,
  Divider,
  Flex,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Tooltip,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';
import { FiBriefcase, FiUsers, FiCalendar, FiEye, FiClock } from 'react-icons/fi';
import { format, parseISO } from 'date-fns';

const JobCard = ({ job, onViewDetails }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'MMM d, yyyy');
    } catch (error) {
      return dateString;
    }
  };
  
  return (
    <Card 
      bg={cardBg} 
      shadow="sm" 
      borderRadius="lg" 
      transition="all 0.2s"
      _hover={{ 
        shadow: "md",
        transform: "translateY(-2px)",
        bg: hoverBg 
      }}
      width="100%"
      height="100%"
      display="flex"
      flexDirection="column"
    >
      <CardHeader pb={2}>
        <HStack spacing={2} mb={1}>
          <Icon as={FiBriefcase} color="blue.500" />
          <Heading size="md" noOfLines={1}>{job.title}</Heading>
        </HStack>
        {job.company && (
          <HStack spacing={2}>
            <Icon as={FiUsers} color="gray.500" />
            <Text color="gray.600" fontSize="sm">{job.company}</Text>
          </HStack>
        )}
      </CardHeader>
      
      <CardBody py={2}>
        <Text noOfLines={3} mb={4} fontSize="sm" color="gray.600">
          {job.description.substring(0, 150)}
          {job.description.length > 150 ? '...' : ''}
        </Text>
        
        <Divider mb={4} />
        
        <VStack align="stretch" spacing={3}>
          {job.required_skills && job.required_skills.length > 0 && (
            <Box>
              <Text fontSize="xs" fontWeight="bold" mb={1}>REQUIRED SKILLS</Text>
              <Wrap spacing={2}>
                {job.required_skills.slice(0, 5).map((skill, index) => (
                  <WrapItem key={index}>
                    <Badge colorScheme="blue">{skill}</Badge>
                  </WrapItem>
                ))}
                {job.required_skills.length > 5 && (
                  <WrapItem>
                    <Badge colorScheme="gray">+{job.required_skills.length - 5} more</Badge>
                  </WrapItem>
                )}
              </Wrap>
            </Box>
          )}
          
          {job.preferred_skills && job.preferred_skills.length > 0 && (
            <Box>
              <Text fontSize="xs" fontWeight="bold" mb={1}>PREFERRED SKILLS</Text>
              <Wrap spacing={2}>
                {job.preferred_skills.slice(0, 3).map((skill, index) => (
                  <WrapItem key={index}>
                    <Badge colorScheme="green" variant="outline">{skill}</Badge>
                  </WrapItem>
                ))}
                {job.preferred_skills.length > 3 && (
                  <WrapItem>
                    <Badge colorScheme="gray" variant="outline">+{job.preferred_skills.length - 3} more</Badge>
                  </WrapItem>
                )}
              </Wrap>
            </Box>
          )}
        </VStack>
      </CardBody>
      
      <CardFooter pt={2} justifyContent="space-between" alignItems="center">
        <HStack spacing={2}>
          <Icon as={FiCalendar} color="gray.500" fontSize="sm" />
          <Text fontSize="xs" color="gray.500">
            Created: {formatDate(job.created_date)}
          </Text>
        </HStack>
        
        <Button
          size="sm"
          rightIcon={<FiEye />}
          colorScheme="blue"
          variant="ghost"
          onClick={() => onViewDetails && onViewDetails(job)}
        >
          View Details
        </Button>
      </CardFooter>
    </Card>
  );
};

export default JobCard;