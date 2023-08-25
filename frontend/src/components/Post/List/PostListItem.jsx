import { Link } from 'react-router-dom';
import cl from './Post.module.css';


const PostListItem = ({post}) => {
    return(
        <Link to={`/posts/${post.id}`} className={cl.postWrapper}>

            <div className={cl.postImageContainer}>
                {post.image
                    ? <img className={cl.postImage} src={`/${post.image}`} alt='post' />
                    : <div className={cl.postNoImage}> No image </div>
                }
            </div>

            <div className={cl.postContentContainer}>
                <div className={cl.postTitle}>
                    {post.title}
                </div>
                <div className={cl.postContent}>
                    {post.content}
                </div>
                <div className={cl.postCreatedAt}>
                    {post.created_at}
                </div>
            </div>

        </Link>
    );
}

export default PostListItem;
