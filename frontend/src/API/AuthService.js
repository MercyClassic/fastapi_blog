import axios from 'axios';


export default class AuthService {
    static async login(data) {
        const response = await axios.post(
            `http://localhost/api/v1/auth/login`,
            {...data},
        )
        return response
    }
}
