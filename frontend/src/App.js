import './static/reset.css';
import './static/style.css';
import { BrowserRouter } from 'react-router-dom';
import AppRouter from './components/AppRouter';
import { AuthContext } from './context/AuthContext';
import { useState, useEffect } from 'react';


function App() {
    const [isAuth, setIsAuth] = useState(false);

    useEffect(() => {
        if (localStorage.getItem('Authorization')) {
            setIsAuth(true)
        }
    }, [localStorage])

    return(
        <AuthContext.Provider value={{
            isAuth,
            setIsAuth,
        }}>

            <BrowserRouter>
                <AppRouter />
            </BrowserRouter>

        </AuthContext.Provider>
    );
}

export default App;
