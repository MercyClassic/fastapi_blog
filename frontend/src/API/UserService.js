import axios from 'axios';


class UserService {
    static async getUsers() {
        const response = await axios.get(
            `/api/v1/users`,
        )
        return response.data
    }

    static async getUser(id) {
        const response = await axios.get(
            `/api/v1/users/${id}`,
        )
        return response.data
    }

    static async register(data) {
        const response = await axios.post(
            `/api/v1/users`,
            {...data},
        )
        return response.data
    }
}

export default UserService;
