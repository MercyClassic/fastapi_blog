import LoginForm from '../components/LoginForm/LoginForm';
import { Link } from 'react-router-dom';


const Login = () => {
    return (
            <div className='centred-container__align-centred'>
                <div className='centred-container'>

                    <div className='centred-container__item'>
                        <div style={{textAlign: 'center'}}>
                            Sign in or <Link to='/registration'> sign up </Link> to create your own post!
                         </div>
                    </div>

                    <div className='centred-container__item'>
                        <LoginForm />
                    </div>

                </div>
            </div>
    );
}

export default Login;
