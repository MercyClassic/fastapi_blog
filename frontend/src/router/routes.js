import { Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import PostList from '../pages/PostList';
import PostDetail from '../pages/PostDetail';
import NotFound from '../pages/NotFound';


const routes = [
    {path: '/', element: <Navigate replace to ="/posts" />, exact: true},
    {path: '/login', element: <Login />, exact: true},
    {path: '/posts', element: <PostList />, exact: true},
    {path: '/posts/:id', element: <PostDetail />, exact: true},
    {path: '/not_found', element: <NotFound />, exact: true},
    {path: '*', element: <Navigate replace to='/not_found' />},
]

export default routes;
