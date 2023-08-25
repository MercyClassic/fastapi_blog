import { Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import PostList from '../pages/PostList';
import PostDetail from '../pages/PostDetail';
import UserList from '../pages/UserList';
import UserDetail from '../pages/UserDetail';
import TagList from '../pages/TagList';
import Registration from '../pages/Registration';
import NotFound from '../pages/NotFound';


const routes = [
    {path: '/', element: <Navigate replace to ="/posts" />, exact: true},
    {path: '/login', element: <Login />, exact: true},
    {path: '/registration', element: <Registration />, exact: true},
    {path: '/posts', element: <PostList />, exact: true},
    {path: '/posts/:id', element: <PostDetail />, exact: true},
    {path: '/tags', element: <TagList />, exact: true},
    {path: '/users/', element: <UserList />, exact: true},
    {path: '/users/:id', element: <UserDetail />, exact: true},
    {path: '/not_found', element: <NotFound />, exact: true},
    {path: '*', element: <Navigate replace to='/not_found' />},
]

export default routes;
