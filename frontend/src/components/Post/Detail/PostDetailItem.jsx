import cl from './Post.module.css';


const PostDetailItem = ({post}) => {
    return(
        <div className={cl.postContainer}>
            <div className={cl.imageContainer}>
                <div>
                    {post.image
                        ? <img src={`/${post.image}`} alt='post' />
                        : <div className=''> No image </div>
                    }
                </div>
            </div>
            <div className={cl.postContentContainer}>
                <div>
                    {post.title}
                </div>
                <div>
                    {post.content}
                </div>
                <div>
                    {post.created_at}
                </div>
            </div>
        </div>
    );
}

export default PostDetailItem;
