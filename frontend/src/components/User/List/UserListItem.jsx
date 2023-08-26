import { Link, useParams } from 'react-router-dom';
import cl from './User.module.css';


const UserListItem = ({user}) => {
    return(
        <div>
            <Link className={cl.userLink} to={`/users/${user.id}`}> {user.username} </Link>
        </div>
    );
}

export default UserListItem;
