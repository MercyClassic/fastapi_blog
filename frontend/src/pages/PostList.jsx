import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import useFetching from '../hooks/useFetching';
import Loader from '../components/Loader/Loader';
import PostService from '../API/PostService';
import PostListItem from '../components/Post/List/PostListItem';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';


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

    if (isLoading) {
        return <Loader />
    }

    return(
        <>
            <Header />
            {posts.length
                ?
                <div className='wrapper'>
                    <div className='container'>
                        <div className='post-list-container'>
                            {posts.map((post) =>
                                <PostListItem post={post} key={post.id}/>
                            )}
                        </div>
                    </div>
                </div>
                :
                <div className='centred-container__align-centred'>
                    <div className='centred-container'>
                        No one post yet
                    </div>
                </div>
            }
            <Footer />
        </>
    );
}

export default PostList;
