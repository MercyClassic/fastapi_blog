import { useState, useEffect } from 'react';
import useFetching from '../hooks/useFetching';
import UserService from '../API/UserService';
import UserListItem from '../components/User/List/UserListItem';
import Loader from '../components/Loader/Loader';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';


const UserList = () => {
    const [users, setUsers] = useState([]);
    const [fetchUsers, isLoading, errorUsers] = useFetching(async () => {
        const response = await UserService.getUsers();
        setUsers(response);
    })

    useEffect(() => {
        fetchUsers();
    }, [])

    if (isLoading) {
        return <Loader />
    }

    return(
        <>
        <Header />
            <div className='centred-container__align-centred'>
                <div className='centred-container'>
                    {users &&
                        users.map((user) =>
                            <UserListItem user={user} key={user.id}/>
                    )}
                </div>
            </div>
        <Footer />
        </>
    );
}

export default UserList;
