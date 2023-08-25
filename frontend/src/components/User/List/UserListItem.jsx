import { Link, useParams } from 'react-router-dom';


const UserListItem = ({user}) => {
    return(
        <div>
            <div>
                <Link to={`/users/${user.id}`}> {user.username} </Link>
            </div>
        </div>
    );
}

export default UserListItem;
