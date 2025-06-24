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
  // --- ИЗМЕНЕНИЕ: Импортируем иконки для админ-разделов ---
  SettingOutlined,
  FileSearchOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { selectCurrentUser, logout } from '../../features/auth/slice';

const { Header, Content, Sider } = Layout;

// --- ИЗМЕНЕНИЕ: Создаем тип для пользователя для большей ясности ---
type User = {
  username: string;
  role: string;
  // ...другие поля пользователя
} | null;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const user: User = useAppSelector(selectCurrentUser);

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login'); // Перенаправление после логаута
  };
  
  // --- ИЗМЕНЕНИЕ: Определяем, является ли пользователь админом/мейнтейнером ---
  const isAdminOrMaintainer = user?.role === 'admin' || user?.role === 'maintainer';

  const userMenuItems: MenuProps['items'] = [
    { 
        key: 'profile', 
        icon: <UserOutlined />, 
        label: <Link to="/profile">Профиль</Link> 
    },
    { 
        type: 'divider',
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
    // Убираем 'Загрузку' из основного меню, т.к. это часть админ-логики или Data Explorer
    // { 
    //     key: '/upload', 
    //     icon: <UploadOutlined />, 
    //     label: <Link to="/upload">Загрузка</Link> 
    // },
    
    // --- ИЗМЕНЕНИЕ: Динамически добавляем админ-меню ---
    isAdminOrMaintainer ? {
        key: '/admin',
        icon: <SettingOutlined />,
        label: 'Администрирование',
        children: [
            {
                key: '/admin/ontology', // Пример вложенного пути
                icon: <ExperimentOutlined />,
                label: <Link to="/ontology">Управление Онтологией</Link>
            },
            {
                key: '/admin/verification', // Пример вложенного пути
                icon: <FileSearchOutlined />,
                label: <Link to="/verification">Верификация</Link>
            },
            // Сюда можно добавить ссылку на панель репарсинга, если она на отдельной странице
        ]
    } : null,
  ].filter(Boolean); // Фильтруем null, если пользователь не админ

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div className="demo-logo-vertical" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)' }} />
        <Menu 
          theme="dark" 
          // --- ИЗМЕНЕНИЕ: location.pathname может не совпадать с ключом, если есть вложенность ---
          // Используем более умное определение активного ключа
          defaultSelectedKeys={[location.pathname]}
          defaultOpenKeys={isAdminOrMaintainer ? ['/admin'] : []} // Открывать админ-меню по умолчанию
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
          <div style={{ padding: 24, minHeight: 360, background: colorBgContainer, borderRadius: borderRadiusLG }}>
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;