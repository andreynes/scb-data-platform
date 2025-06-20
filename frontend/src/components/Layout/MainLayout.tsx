// frontend/src/components/Layout/MainLayout.tsx
import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, theme } from 'antd';
import type { MenuProps } from 'antd';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  UserOutlined,
  LogoutOutlined,
  DatabaseOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { selectCurrentUser, logout } from '../../features/auth/slice';

const { Header, Content, Sider } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const user = useAppSelector(selectCurrentUser);

  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const userMenuItems: MenuProps['items'] = [
    { 
        key: 'profile', 
        icon: <UserOutlined />, 
        label: <Link to="/profile">Профиль</Link> 
    },
    { 
        key: 'logout', 
        icon: <LogoutOutlined />, 
        label: 'Выход', 
        onClick: handleLogout 
    },
  ];
  
  const mainMenuItems: MenuProps['items'] = [
    { 
        key: '/data-explorer', 
        icon: <DatabaseOutlined />, 
        label: <Link to="/data-explorer">Исследователь Данных</Link> 
    },
    { 
        key: '/upload', 
        icon: <UploadOutlined />, 
        label: <Link to="/upload">Загрузка</Link> 
    },
    // Сюда можно будет добавить другие пункты меню
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div className="demo-logo-vertical" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)' }} />
        <Menu 
          theme="dark" 
          selectedKeys={[location.pathname]} 
          mode="inline" 
          items={mainMenuItems} 
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: colorBgContainer, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          {user ? (
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <a onClick={(e) => e.preventDefault()}>
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar icon={<UserOutlined />} />
                  {user.username}
                </Space>
              </a>
            </Dropdown>
          ) : null}
        </Header>
        <Content style={{ margin: '16px' }}>
          <div style={{ padding: 24, minHeight: 360, background: colorBgContainer }}>
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;