import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Divider,
  SimpleGrid,
  Icon,
  List,
  ListItem,
  ListIcon,
  Heading,
  Card,
  CardBody,
  useColorModeValue
} from '@chakra-ui/react';
import { FiUser, FiMail, FiPhone, FiBook, FiCode, FiBriefcase, FiCheckCircle, FiFileText } from 'react-icons/fi';

const ParsedCVView = ({ cvData }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  if (!cvData) return null;
  
  return (
    <Box w="100%">
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
        {/* Personal Information */}
        <Card bg={cardBg} shadow="sm" borderRadius="lg">
          <CardBody>
            <VStack align="start" spacing={3}>
              <Heading size="sm" display="flex" alignItems="center">
                <Icon as={FiUser} mr={2} />
                Personal Information
              </Heading>
              <Divider />
              
              <Box width="100%">
                <HStack mb={2}>
                  <Text fontWeight="bold" minWidth="100px">Name:</Text>
                  <Text>{cvData.name || 'Not detected'}</Text>
                </HStack>
                
                <HStack mb={2}>
                  <Text fontWeight="bold" minWidth="100px">Email:</Text>
                  <Text>{cvData.email || 'Not detected'}</Text>
                </HStack>
                
                <HStack mb={2}>
                  <Text fontWeight="bold" minWidth="100px">Phone:</Text>
                  <Text>{cvData.phone || 'Not detected'}</Text>
                </HStack>
                
                <HStack>
                  <Text fontWeight="bold" minWidth="100px">File:</Text>
                  <Text>{cvData.file_name}</Text>
                </HStack>
              </Box>
            </VStack>
          </CardBody>
        </Card>
        
        {/* Skills */}
        <Card bg={cardBg} shadow="sm" borderRadius="lg">
          <CardBody>
            <VStack align="start" spacing={3}>
              <Heading size="sm" display="flex" alignItems="center">
                <Icon as={FiCode} mr={2} />
                Skills
              </Heading>
              <Divider />
              
              <Box width="100%">
                {cvData.skills && cvData.skills.length > 0 ? (
                  <Box display="flex" flexWrap="wrap" gap={2}>
                    {cvData.skills.map((skill, index) => (
                      <Badge key={index} colorScheme="blue" px={2} py={1}>
                        {skill}
                      </Badge>
                    ))}
                  </Box>
                ) : (
                  <Text color="gray.500">No skills detected</Text>
                )}
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>
      
      {/* Education */}
      <Card bg={cardBg} shadow="sm" borderRadius="lg" mb={6}>
        <CardBody>
          <VStack align="start" spacing={3}>
            <Heading size="sm" display="flex" alignItems="center">
              <Icon as={FiBook} mr={2} />
              Education
            </Heading>
            <Divider />
            
            {cvData.education && cvData.education.length > 0 ? (
              <List spacing={2} width="100%">
                {cvData.education.map((edu, index) => (
                  <ListItem key={index}>
                    <ListIcon as={FiCheckCircle} color="green.500" />
                    {edu}
                  </ListItem>
                ))}
              </List>
            ) : (
              <Text color="gray.500">No education history detected</Text>
            )}
          </VStack>
        </CardBody>
      </Card>
      
      {/* Experience */}
      <Card bg={cardBg} shadow="sm" borderRadius="lg">
        <CardBody>
          <VStack align="start" spacing={3}>
            <Heading size="sm" display="flex" alignItems="center">
              <Icon as={FiBriefcase} mr={2} />
              Work Experience
            </Heading>
            <Divider />
            
            {cvData.experience && cvData.experience.length > 0 ? (
              <List spacing={3} width="100%">
                {cvData.experience.map((exp, index) => (
                  <ListItem key={index} p={2} borderLeft="2px solid" borderColor="blue.500" pl={4}>
                    <Text>{exp.description}</Text>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Text color="gray.500">No work experience detected</Text>
            )}
          </VStack>
        </CardBody>
      </Card>
    </Box>
  );
};

export default ParsedCVView;