import React, { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Progress,
  Badge,
  Divider,
  Icon,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  List,
  ListItem,
  ListIcon,
  Card,
  CardBody,
  CardHeader,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Flex,
  Wrap,
  WrapItem,
  Tag,
  useColorModeValue
} from '@chakra-ui/react';
import {
  FiCheckCircle,
  FiXCircle,
  FiUserCheck,
  FiCode,
  FiBook,
  FiBriefcase,
  FiAward,
  FiAlertCircle,
  FiTrendingUp
} from 'react-icons/fi';
import SkillsMatchChart from './SkillsMatchChart';

const MatchResultItem = ({ match, index }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const accentBg = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.600');
  
  // Determine score color
  const getScoreColor = (score) => {
    if (score >= 80) return "green";
    if (score >= 60) return "blue";
    if (score >= 40) return "orange";
    return "red";
  };
  
  const overallScoreColor = getScoreColor(match.overall_score);
  
  return (
    <Card 
      bg={cardBg} 
      shadow="sm" 
      borderRadius="lg"
      borderLeft="5px solid"
      borderColor={overallScoreColor + ".500"}
    >
      <CardHeader pb={2}>
        <HStack justify="space-between" align="flex-start" mb={2}>
          <VStack align="start" spacing={0}>
            <Heading size="md">{match.resume_name || "Candidate"}</Heading>
            <Text fontSize="sm" color="gray.500">{match.resume_id}</Text>
          </VStack>
          
          <Stat textAlign="right" width="auto">
            <StatLabel fontSize="xs">Overall Match</StatLabel>
            <StatNumber fontSize="2xl" color={`${overallScoreColor}.500`}>
              {match.overall_score}%
            </StatNumber>
          </Stat>
        </HStack>
        
        <Divider mb={3} />
        
        <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={3}>
          <Stat size="sm" bg={accentBg} p={2} borderRadius="md">
            <StatLabel fontSize="xs" display="flex" alignItems="center">
              <Icon as={FiCode} mr={1} />
              Skills Match
            </StatLabel>
            <StatNumber fontSize="lg" color={getScoreColor(match.skills_score) + ".500"}>
              {match.skills_score}%
            </StatNumber>
          </Stat>
          
          <Stat size="sm" bg={accentBg} p={2} borderRadius="md">
            <StatLabel fontSize="xs" display="flex" alignItems="center">
              <Icon as={FiBook} mr={1} />
              Education
            </StatLabel>
            <StatNumber fontSize="lg" color={getScoreColor(match.education_score) + ".500"}>
              {match.education_score}%
            </StatNumber>
          </Stat>
          
          <Stat size="sm" bg={accentBg} p={2} borderRadius="md">
            <StatLabel fontSize="xs" display="flex" alignItems="center">
              <Icon as={FiBriefcase} mr={1} />
              Experience
            </StatLabel>
            <StatNumber fontSize="lg" color={getScoreColor(match.experience_score) + ".500"}>
              {match.experience_score}%
            </StatNumber>
          </Stat>
          
          <Stat size="sm" bg={accentBg} p={2} borderRadius="md">
            <StatLabel fontSize="xs" display="flex" alignItems="center">
              <Icon as={FiTrendingUp} mr={1} />
              Keyword Match
            </StatLabel>
            <StatNumber fontSize="lg" color={getScoreColor(match.keyword_match_score) + ".500"}>
              {match.keyword_match_score}%
            </StatNumber>
          </Stat>
        </SimpleGrid>
      </CardHeader>
      
      <CardBody pt={0}>
        <Accordion allowToggle mt={4}>
          <AccordionItem border="none">
            <AccordionButton 
              bg={accentBg} 
              _hover={{ bg: hoverBg }}
              borderRadius="md"
            >
              <Box flex="1" textAlign="left" fontWeight="medium">
                View Match Details
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel pb={4} pt={4}>
              <VStack spacing={4} align="stretch">
                {/* Skills breakdown */}
                <Box>
                  <Heading size="sm" mb={3} display="flex" alignItems="center">
                    <Icon as={FiCode} mr={2} />
                    Skills Analysis
                  </Heading>
                  
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={2}>Matched Skills ({match.matched_skills.length})</Text>
                      {match.matched_skills.length > 0 ? (
                        <Wrap spacing={2}>
                          {match.matched_skills.map((skill, i) => (
                            <WrapItem key={i}>
                              <Tag colorScheme="green" size="sm" borderRadius="full">
                                <Icon as={FiCheckCircle} mr={1} />
                                {skill}
                              </Tag>
                            </WrapItem>
                          ))}
                        </Wrap>
                      ) : (
                        <Text fontSize="sm" color="gray.500">No matched skills found</Text>
                      )}
                    </Box>
                    
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={2}>Missing Skills ({match.missing_skills.length})</Text>
                      {match.missing_skills.length > 0 ? (
                        <Wrap spacing={2}>
                          {match.missing_skills.map((skill, i) => (
                            <WrapItem key={i}>
                              <Tag colorScheme="red" size="sm" borderRadius="full" variant="outline">
                                <Icon as={FiXCircle} mr={1} />
                                {skill}
                              </Tag>
                            </WrapItem>
                          ))}
                        </Wrap>
                      ) : (
                        <Text fontSize="sm" color="gray.500">No missing skills found</Text>
                      )}
                    </Box>
                  </SimpleGrid>
                </Box>
                
                <Divider />
                
                {/* Education & Experience */}
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <Box>
                    <Heading size="sm" mb={3} display="flex" alignItems="center">
                      <Icon as={FiBook} mr={2} />
                      Education Match
                    </Heading>
                    
                    {match.matched_education.length > 0 ? (
                      <List spacing={1}>
                        {match.matched_education.map((edu, i) => (
                          <ListItem key={i} display="flex" alignItems="flex-start">
                            <ListIcon as={FiCheckCircle} color="green.500" mt={1} />
                            <Text fontSize="sm">{edu}</Text>
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Text fontSize="sm" color="gray.500">No matched education requirements</Text>
                    )}
                  </Box>
                  
                  <Box>
                    <Heading size="sm" mb={3} display="flex" alignItems="center">
                      <Icon as={FiBriefcase} mr={2} />
                      Experience Match
                    </Heading>
                    
                    {match.matched_experience_keywords.length > 0 ? (
                      <List spacing={1}>
                        {match.matched_experience_keywords.map((exp, i) => (
                          <ListItem key={i} display="flex" alignItems="flex-start">
                            <ListIcon as={FiCheckCircle} color="green.500" mt={1} />
                            <Text fontSize="sm">{exp}</Text>
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Text fontSize="sm" color="gray.500">No matched experience requirements</Text>
                    )}
                  </Box>
                </SimpleGrid>
                
                {/* Skills match chart */}
                <Box mt={3}>
                  <Heading size="sm" mb={4} textAlign="center">Skills Match Visualization</Heading>
                  <SkillsMatchChart match={match} height={200} />
                </Box>
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </CardBody>
    </Card>
  );
};

const MatchResults = ({ results, jobTitle }) => {
  const resultCardBg = useColorModeValue('blue.50', 'blue.900');
  
  if (!results || results.length === 0) {
    return null;
  }
  
  return (
    <Box>
      <Card mb={6} bg={resultCardBg} borderRadius="lg" p={4} shadow="md">
        <HStack>
          <Icon as={FiAward} boxSize={6} color="blue.500" />
          <Box>
            <Heading size="md">Match Results</Heading>
            <Text mt={1}>
              {results.length} CVs matched against "{jobTitle}"
            </Text>
          </Box>
        </HStack>
      </Card>
      
      <VStack spacing={6} align="stretch">
        {results.map((match, index) => (
          <MatchResultItem key={match.resume_id} match={match} index={index} />
        ))}
      </VStack>
    </Box>
  );
};

export default MatchResults;