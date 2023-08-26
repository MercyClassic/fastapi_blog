import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import useFetching from '../hooks/useFetching';
import PostService from '../API/PostService';
import PostDetailItem from '../components/Post/Detail/PostDetailItem';
import Loader from '../components/Loader/Loader';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';


const PostDetail = () => {
    const [post, setPost] = useState({});
    const params = useParams();
    const [fetchPost, isLoading, errorPost] = useFetching(async () => {
        const response = await PostService.getPost(params.id);
        setPost(response);
    })

    useEffect(() => {
        fetchPost()
    }, [])

    if (isLoading) {
        return <Loader />
    }

    return(
        <>
        <Header />
            <div className='centred-container'>
                <div className='centred-container__align-centred'>
                    <PostDetailItem post={post} />
                </div>
            </div>
        <Footer />
        </>
    );
}

export default PostDetail;
