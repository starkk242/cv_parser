import React from 'react';
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  useDisclosure,
  useColorModeValue,
  Stack,
  Text,
  Icon,
  Heading,
  useColorMode
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  FiMenu,
  FiX,
  FiFileText,
  FiBriefcase,
  FiSearch,
  FiUser,
  FiLogOut,
  FiMoon,
  FiSun,
  FiHome,
  FiSettings
} from 'react-icons/fi';

const NavLink = ({ children, to, icon, isActive }) => {
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.700', 'blue.200');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  
  return (
    <RouterLink to={to}>
      <Button
        px={4}
        py={2}
        rounded={'md'}
        bg={isActive ? activeBg : 'transparent'}
        color={isActive ? activeColor : undefined}
        leftIcon={icon}
        variant="ghost"
        _hover={{
          bg: isActive ? activeBg : hoverBg,
        }}
      >
        {children}
      </Button>
    </RouterLink>
  );
};

const Navbar = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  const location = useLocation();
  
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <FiHome /> },
    { name: 'CV Parser', path: '/cv-parser', icon: <FiFileText /> },
    { name: 'Job Descriptions', path: '/jobs', icon: <FiBriefcase /> },
    { name: 'Match CVs', path: '/match', icon: <FiSearch /> },
  ];
  
  return (
    <Box bg={useColorModeValue('white', 'gray.900')} px={4} boxShadow="sm">
      <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
        <IconButton
          size={'md'}
          icon={isOpen ? <FiX /> : <FiMenu />}
          aria-label={'Open Menu'}
          display={{ md: 'none' }}
          onClick={isOpen ? onClose : onOpen}
        />
        <HStack spacing={8} alignItems={'center'}>
          <Box>
            <Heading size="md" color={useColorModeValue('blue.600', 'blue.200')}>
              CV-Match
            </Heading>
          </Box>
          <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
            {navItems.map((item) => (
              <NavLink 
                key={item.path} 
                to={item.path} 
                icon={item.icon}
                isActive={location.pathname === item.path}
              >
                {item.name}
              </NavLink>
            ))}
          </HStack>
        </HStack>
        
        <Flex alignItems={'center'}>
          <Button
            variant="ghost"
            onClick={toggleColorMode}
            mr={2}
            aria-label="Toggle color mode"
          >
            {colorMode === 'light' ? <FiMoon /> : <FiSun />}
          </Button>
          
          <Menu>
            <MenuButton
              as={Button}
              rounded={'full'}
              variant={'link'}
              cursor={'pointer'}
              minW={0}
            >
              <Button leftIcon={<FiUser />} colorScheme="blue" variant="outline">
                Profile
              </Button>
            </MenuButton>
            <MenuList>
              <MenuItem icon={<FiUser />}>Profile</MenuItem>
              <MenuItem icon={<FiSettings />}>Settings</MenuItem>
              <MenuDivider />
              <MenuItem icon={<FiLogOut />}>Sign Out</MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </Flex>

      {isOpen ? (
        <Box pb={4} display={{ md: 'none' }}>
          <Stack as={'nav'} spacing={4}>
            {navItems.map((item) => (
              <NavLink 
                key={item.path} 
                to={item.path} 
                icon={item.icon}
                isActive={location.pathname === item.path}
              >
                {item.name}
              </NavLink>
            ))}
          </Stack>
        </Box>
      ) : null}
    </Box>
  );
};

export default Navbar;