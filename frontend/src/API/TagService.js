import axios from 'axios';


class TagService {
    static async getTags() {
        const response = await axios.get(
            `/api/v1/tags`,
        )
        return response.data
    }
}

export default TagService;
