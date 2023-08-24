import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import useFetching from '../hooks/useFetching';
import Loader from '../components/Loader/Loader';
import PostService from '../API/PostService';
import PostListItem from '../components/Post/PostListItem';


const PostList = () => {
    const [posts, setPosts] = useState([]);
    const [fetchPosts, isLoading, errorPosts] = useFetching(async () => {
        const response = await PostService.getPosts();
        setPosts(response);
    });
    const location = useLocation();

    useEffect(() => {
        fetchPosts();
    }, [location.search])

    return(
        <>
            {isLoading && <Loader /> && console.log(posts)}
            {posts
                ? <div className='centred-container__align-centred'>
                    <div className='centred-container'>
                        {posts.map((post) =>
                            <PostListItem post={post} key={post.id}/>
                        )}
                    </div>
                  </div>

                : <div className='centred-container__align-centred'>
                    <div className='centred-container'>
                        No one post yet
                    </div>
                  </div>
            }
        </>
    );
}

export default PostList;
