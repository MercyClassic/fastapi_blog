import axios from 'axios';


export default class AuthService {
    static async login(data) {
        const response = await axios.post(
            `http://localhost/api/v1/auth/login`,
            {...data},
        )
        return response
    }

    static async refreshToken() {
        const response = await axios.post(
            `http://localhost/api/v1/auth/refresh_token`,
        )
        return response.data.access_token;
    }

    static async logout() {
        const response = await axios.post(
            `http://localhost/api/v1/auth/logout`,
        )
    }
}
