import React from 'react';
import { Box, Container, Flex, useColorModeValue } from '@chakra-ui/react';
import Navbar from '../components/common/Navbar';

const MainLayout = ({ children }) => {
  return (
    <Flex
      direction="column"
      minH="100vh"
      bg={useColorModeValue('gray.50', 'gray.900')}
    >
      <Navbar />
      <Box flex="1" py={8}>
        <Container maxW="container.xl">
          {children}
        </Container>
      </Box>
      <Box as="footer" py={4} textAlign="center" fontSize="sm" color="gray.500">
        &copy; {new Date().getFullYear()} CV-Match. All rights reserved.
      </Box>
    </Flex>
  );
};

export default MainLayout;