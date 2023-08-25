import { useState } from 'react';
import AuthService from '../API/AuthService';


const useFetching = (callback) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(false);

    const fetching = async (data=null) => {
        try {
            setIsLoading(true);
            await callback(data);
        } catch (e) {
            if (e.request.status === 401) {
                const token = await AuthService.refreshToken();
                localStorage.setItem('Authorization', token);
                try {
                    await callback(data);
                } catch (ex) {}
            }
            setError(e.request);
        } finally {
            setIsLoading(false);
        }
    }

    return [fetching, isLoading, error]
}

export default useFetching;
