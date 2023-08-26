import { useContext } from 'react';
import { Link } from 'react-router-dom';
import cl from './Header.module.css';
import AuthService from '../../API/AuthService';
import { AuthContext } from '../../context/AuthContext';


const Header = () => {
    const {isAuth, setIsAuth} = useContext(AuthContext);

    const logout = async () => {
        if (!isAuth) {
            return null;
        }
        try {
            await AuthService.logout();
        } catch (e) {
            if (e.request.status === 401) {
                localStorage.removeItem('Authorization');
                setIsAuth(false);
            }
        }
    }

    return(
        <header className={cl.header}>
            <ul className={cl.menu}>
                <li className={cl.menuItem} >
                    <Link to='/posts'> All Posts </Link>
                </li>
                <li className={cl.menuItem} >
                    <Link to='/users'> All Users </Link>
                </li>
                {isAuth
                    ?
                    <li className={cl.menuItem} onClick={(e) => logout(e)}>
                        Logout
                    </li>
                    :
                    <li className={cl.menuItem}>
                        <Link to='/login'> Sign in / Sign ip </Link>
                    </li>
                }

            </ul>
        </header>
    );
}

export default Header;
