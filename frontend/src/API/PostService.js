import axios from 'axios';


class PostService {
    static async getPosts() {
        const response = await axios.get(
            `http://localhost/api/v1/posts`,
        );
        return response.data
    }

   static async getPost(id) {
        const response = await axios.get(
            `http://localhost/api/v1/posts/${id}`,
        );
        return response.data
   }

   static async createPost(data) {
        const response = await axios.get(
            `http://localhost/api/v1/posts`,
            {...data}
        );
        return response.data
   }

   static async editPost(id, data) {
       const response = await axios.get(
            `http://localhost/api/v1/posts/${id}`,
            {...data},
       );
       return response.data
   }

   static async deletePost(id) {
       const response = await axios.get(
            `http://localhost/api/v1/posts/${id}`,
       );
       return response.data
   }
}

export default PostService;
