import React, { useState, useRef } from 'react';
import { Box, Button, Text, VStack, HStack, Icon, Progress, useColorModeValue } from '@chakra-ui/react';
import { FiFile, FiUpload, FiX } from 'react-icons/fi';

const FileUpload = ({ 
  accept = '.pdf,.docx,.txt', 
  multiple = true, 
  onChange, 
  maxSize = 10, // in MB
  maxFiles = 10,
  height = "200px"
}) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const boxBg = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const dragBorderColor = useColorModeValue('blue.400', 'blue.300');

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const validateFile = (file) => {
    // Check file size (convert maxSize from MB to bytes)
    if (file.size > maxSize * 1024 * 1024) {
      return `File too large. Maximum size is ${maxSize}MB.`;
    }
    
    // Check file type
    const fileType = file.name.split('.').pop().toLowerCase();
    const acceptedTypes = accept.split(',').map(type => 
      type.trim().replace('.', '').toLowerCase()
    );
    
    if (!acceptedTypes.includes(fileType)) {
      return `Invalid file type. Accepted types: ${accept}`;
    }
    
    return null;
  };

  const processFiles = (fileList) => {
    const newFiles = [];
    const errors = [];
    
    // Check if adding these files would exceed the max file limit
    if (files.length + fileList.length > maxFiles) {
      errors.push(`Cannot upload more than ${maxFiles} files.`);
      return { newFiles, errors };
    }
    
    // Process each file
    Array.from(fileList).forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(`${file.name}: ${error}`);
      } else {
        newFiles.push(file);
      }
    });
    
    return { newFiles, errors };
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const { newFiles, errors } = processFiles(e.dataTransfer.files);
    
    if (errors.length > 0) {
      // Display errors (you might want to use a toast or alert component)
      errors.forEach(error => console.error(error));
    }
    
    if (newFiles.length > 0) {
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      if (onChange) onChange(updatedFiles);
    }
  };

  const handleFileInputChange = (e) => {
    const { newFiles, errors } = processFiles(e.target.files);
    
    if (errors.length > 0) {
      // Display errors
      errors.forEach(error => console.error(error));
    }
    
    if (newFiles.length > 0) {
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      if (onChange) onChange(updatedFiles);
    }
    
    // Reset the file input
    e.target.value = null;
  };

  const handleRemoveFile = (index) => {
    const updatedFiles = [...files];
    updatedFiles.splice(index, 1);
    setFiles(updatedFiles);
    if (onChange) onChange(updatedFiles);
  };

  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      case 'txt':
        return '📃';
      default:
        return '📎';
    }
  };

  return (
    <VStack spacing={4} width="100%">
      <Box
        border="2px dashed"
        borderColor={isDragging ? dragBorderColor : borderColor}
        borderRadius="md"
        bg={boxBg}
        p={4}
        width="100%"
        height={height}
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        transition="border-color 0.2s"
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
        cursor="pointer"
      >
        <Icon as={FiUpload} boxSize={10} color={isDragging ? "blue.500" : "gray.500"} mb={2} />
        <Text fontWeight="medium" mb={1}>
          {isDragging ? "Drop files here" : "Drag & drop files here"}
        </Text>
        <Text fontSize="sm" color="gray.500">
          or click to browse
        </Text>
        <Text fontSize="xs" color="gray.500" mt={2}>
          Accepted formats: {accept} (Max size: {maxSize}MB)
        </Text>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInputChange}
          accept={accept}
          multiple={multiple}
          style={{ display: 'none' }}
        />
      </Box>

      {files.length > 0 && (
        <Box width="100%" borderRadius="md" border="1px solid" borderColor={borderColor} p={3}>
          <Text fontWeight="medium" mb={2}>
            Selected Files ({files.length}/{maxFiles})
          </Text>
          <Progress value={(files.length / maxFiles) * 100} size="sm" mb={3} colorScheme="blue" />
          <VStack spacing={2} align="stretch" maxHeight="200px" overflowY="auto">
            {files.map((file, index) => (
              <HStack key={index} p={2} bg={boxBg} borderRadius="md" justify="space-between">
                <HStack>
                  <Text fontSize="xl">{getFileIcon(file.name)}</Text>
                  <VStack spacing={0} align="start">
                    <Text fontSize="sm" fontWeight="medium" noOfLines={1}>{file.name}</Text>
                    <Text fontSize="xs" color="gray.500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </Text>
                  </VStack>
                </HStack>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  colorScheme="red" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile(index);
                  }}
                >
                  <Icon as={FiX} />
                </Button>
              </HStack>
            ))}
          </VStack>
        </Box>
      )}
    </VStack>
  );
};

export default FileUpload;