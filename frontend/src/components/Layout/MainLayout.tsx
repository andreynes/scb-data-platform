// Файл: frontend/src/components/Layout/MainLayout.tsx

import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, theme } from 'antd';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import type { MenuProps } from 'antd';
import {
    UserOutlined,
    LogoutOutlined,
    DatabaseOutlined,
    CheckCircleOutlined,
    ApartmentOutlined, // Иконка для Онтологии
} from '@ant-design/icons';

// Импортируем хуки и селекторы для получения данных пользователя и статуса
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { selectCurrentUser, logoutAction } from '../../features/auth/slice';

const { Header, Content, Sider } = Layout;

const MainLayout: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    
    // Получаем текущего пользователя из Redux store
    const user = useAppSelector(selectCurrentUser);

    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    // Обработчик выхода из системы
    const handleLogout = () => {
        dispatch(logoutAction());
        // useNavigate() предпочтительнее, чем прямое изменение window.location
        navigate('/login');
    };

    // === ИЗМЕНЕНО: Формируем меню динамически в зависимости от роли ===
    
    // Базовые пункты меню, доступные всем
    const baseMenuItems: MenuProps['items'] = [
        { 
            key: '/data-explorer', 
            icon: <DatabaseOutlined />, 
            label: <Link to="/data-explorer">Исследователь</Link> 
        },
        { 
            key: '/profile', 
            icon: <UserOutlined />, 
            label: <Link to="/profile">Профиль</Link> 
        },
    ];

    // Пункты меню только для админов/мейнтейнеров
    const adminMenuItems: MenuProps['items'] = [
        {
            key: 'admin-group', // Используем ключ для группы
            icon: <ApartmentOutlined />,
            label: 'Администрирование',
            children: [
                { 
                    key: '/verification', 
                    icon: <CheckCircleOutlined />, 
                    label: <Link to="/verification">Верификация</Link> 
                },
                { 
                    key: '/ontology', 
                    icon: <ApartmentOutlined />, 
                    label: <Link to="/ontology">Онтология</Link> 
                },
            ],
        },
    ];

    // Собираем финальное меню
    const menuItems = [
        ...baseMenuItems,
        ...(user?.role === 'admin' || user?.role === 'maintainer' ? adminMenuItems : []),
    ];

    // Меню для выпадающего списка пользователя
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

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
                <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)' }} />
                <Menu
                    theme="dark"
                    mode="inline"
                    // Определяем активный пункт на основе URL
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                />
            </Sider>
            <Layout>
                <Header style={{ padding: '0 16px', background: colorBgContainer, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    {user ? (
                        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                            <Space style={{ cursor: 'pointer' }}>
                                <Avatar icon={<UserOutlined />} />
                                {user.username}
                            </Space>
                        </Dropdown>
                    ) : null}
                </Header>
                <Content style={{ margin: '16px' }}>
                    <div
                        style={{
                            padding: 24,
                            minHeight: 360,
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                        }}
                    >
                        <Outlet /> {/* Здесь рендерятся дочерние маршруты */}
                    </div>
                </Content>
            </Layout>
        </Layout>
    );
};

export default MainLayout;