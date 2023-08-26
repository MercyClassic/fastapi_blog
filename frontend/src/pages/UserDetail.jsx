import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import useFetching from '../hooks/useFetching';
import UserService from '../API/UserService';
import Loader from '../components/Loader/Loader';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';


const UserDetail = () => {
    const [user, setUsers] = useState({});
    const params = useParams();

    const [fetchUser, isLoading, errorUsers] = useFetching(async () => {
        const response = await UserService.getUser(params.id);
        setUsers(response);
    })

    useEffect(() => {
        fetchUser();
    }, [])

    if (isLoading) {
        return <Loader />
    }

    return(
        <>
            <Header />
                <div>
                    {user.username}
                </div>
            <Footer />
        </>
    );
}

export default UserDetail;
