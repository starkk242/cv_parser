import React from 'react';
import {
  Box,
  Heading,
  Text,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Icon,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FiHome, FiFileText } from 'react-icons/fi';
import CVUploader from '../components/cv/CVUploader';

const CVParser = () => {
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
            <Icon as={FiFileText} mr={1} />
            CV Parser
          </BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>
      
      <Box mb={8}>
        <Heading mb={2}>CV Parser</Heading>
        <Text color="gray.600">
          Upload and parse CV/Resume files to extract structured information such as contact details, skills, education, and work experience.
        </Text>
      </Box>
      
      <CVUploader />
    </Box>
  );
};

export default CVParser;