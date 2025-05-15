import React, { useState } from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  HStack,
  useToast,
  Spinner,
  Icon,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Divider,
  Tabs, TabList, TabPanels, Tab, TabPanel,
  useColorModeValue
} from '@chakra-ui/react';
import { FiDownload, FiUpload, FiFileText, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import FileUpload from '../common/FileUpload';
import { uploadCV, downloadParsedCVs } from '../../api/cv';
import ParsedCVView from './ParsedCVView';

const CVUploader = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [parsedData, setParsedData] = useState([]);
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  
  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        title: 'No files selected',
        description: 'Please select at least one CV to upload.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setUploading(true);
    try {
      const data = await uploadCV(files);
      setParsedData(data);
      toast({
        title: 'CVs uploaded successfully',
        description: `${files.length} CV(s) parsed successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: 'Upload failed',
        description: error.detail || 'An error occurred while uploading the CVs.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setUploading(false);
    }
  };
  
  const handleDownloadExcel = async () => {
    if (files.length === 0) {
      toast({
        title: 'No files selected',
        description: 'Please select at least one CV to download.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setDownloading(true);
    try {
      await downloadParsedCVs(files);
      toast({
        title: 'Excel file downloaded',
        description: 'Your parsed CV data has been downloaded as an Excel file.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Download error:', error);
      toast({
        title: 'Download failed',
        description: error.detail || 'An error occurred while generating the Excel file.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setDownloading(false);
    }
  };
  
  return (
    <Box width="100%">
      <Card bg={cardBg} shadow="md" borderRadius="lg" mb={6}>
        <CardHeader>
                    <Heading size="md">
            <Icon as={FiFileText} mr={2} />
            CV Parser
          </Heading>
          <Text mt={2} color="gray.600">
            Upload CV/Resume files to extract key information such as contact details, skills, education, and experience.
          </Text>
        </CardHeader>
        <CardBody>
          <FileUpload 
            accept=".pdf,.docx,.txt" 
            multiple={true} 
            onChange={setFiles}
            maxSize={10}
            maxFiles={20}
          />
        </CardBody>
        <Divider />
        <CardFooter>
          <HStack spacing={4}>
            <Button 
              leftIcon={<FiUpload />} 
              colorScheme="blue" 
              onClick={handleUpload}
              isLoading={uploading}
              loadingText="Parsing..."
              isDisabled={files.length === 0 || downloading}
            >
              Parse CVs
            </Button>
            <Button 
              leftIcon={<FiDownload />} 
              colorScheme="green" 
              variant="outline"
              onClick={handleDownloadExcel}
              isLoading={downloading}
              loadingText="Downloading..."
              isDisabled={files.length === 0 || uploading}
            >
              Download as Excel
            </Button>
          </HStack>
        </CardFooter>
      </Card>

      {parsedData.length > 0 && (
        <Card bg={cardBg} shadow="md" borderRadius="lg">
          <CardHeader>
            <Heading size="md">
              <Icon as={FiCheckCircle} mr={2} color="green.500" />
              Parsed Results
            </Heading>
            <Text mt={2} color="gray.600">
              {parsedData.length} CV(s) successfully parsed.
            </Text>
          </CardHeader>
          <Divider />
          <CardBody>
            <Tabs variant="soft-rounded" colorScheme="blue">
              <TabList mb={4} overflowX="auto" py={2}>
                {parsedData.map((cv, index) => (
                  <Tab key={index} minWidth="150px">
                    {cv.name || `CV ${index + 1}`}
                  </Tab>
                ))}
              </TabList>
              <TabPanels>
                {parsedData.map((cv, index) => (
                  <TabPanel key={index} p={0}>
                    <ParsedCVView cvData={cv} />
                  </TabPanel>
                ))}
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>
      )}
    </Box>
  );
};

export default CVUploader;