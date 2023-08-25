import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import useFetching from '../hooks/useFetching';
import UserService from '../API/UserService';
import Loader from '../components/Loader/Loader';


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
            <div>
                {user.username}
            </div>
        </>
    );
}

export default UserDetail;
