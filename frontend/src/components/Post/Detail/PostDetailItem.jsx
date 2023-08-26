import cl from './Post.module.css';


const TagDetail = ({tag}) => {
    return(
        <div className={cl.tag}>
            <div className={cl.tagTitle}> {tag.name} </div>
        </div>
    )
}


const PostDetailItem = ({post}) => {
    return(
        <div className={cl.postContainer}>

            <div className={cl.imageContainer}>
                {post.image
                    ? <img src={`/${post.image}`} alt='post' />
                    : <div className={cl.noImage}> No image </div>
                }
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

            <div className={cl.tagListContainer}>
                {post.tags &&
                    post.tags.map((tag) =>
                        <TagDetail tag={tag} key={tag.id} />
                )}
            </div>
        </div>
    );
}

export default PostDetailItem;
