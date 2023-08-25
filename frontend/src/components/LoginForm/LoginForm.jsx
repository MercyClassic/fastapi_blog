import { useNavigate } from 'react-router-dom';
import Loader from '../Loader/Loader';
import AuthService from '../../API/AuthService';
import useFetching from '../../hooks/useFetching';
import cl from './LoginForm.module.css';


const LoginForm = () => {
    const navigate = useNavigate();

     const [login, isLoading, errorLogin] = useFetching(async (event) => {
        event.preventDefault();
        const form = event.target.closest('form');
        const email = form.email.value;
        const input_password = form.input_password.value;

        if (email === '' || input_password === '') {
            alert('Fill in the required fields');
            return null;
        }

        const response = await AuthService.login({email, input_password});
        if (response.status === 200) {
            localStorage.setItem('Authorization', response.data.access_token);
            alert('You successfully authorized!');
            navigate('/');
        }
    })

    if (isLoading) {
        return <Loader />
    }

    return (
        <>
        <div className={cl.loginFormContainer}>
            <form className={cl.loginForm}>
                <label htmlFor='email'> Email: </label>
                <input name='email' />
                <label htmlFor='input_password'> Password: </label>
                <input name='input_password' />
                <button type="button" className={cl.signInButton} onClick={(e) => login(e)}> Sign in </button>
            </form>
        </div>
        </>
    );
}

export default LoginForm;
