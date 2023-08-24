import cl from './Post.module.css';


const PostListItem = ({post}) => {
    return(
        <div className={cl.post}>
            {post.image &&
                <div className={cl.postImage}>
                    <img height='100px' width='100px' src={`http://localhost/${post.image}`} alt='post' />
                </div>
            }
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
    );
}

export default PostListItem;
