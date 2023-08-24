import { useState } from 'react';

const useFetching = (callback) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(false);

    const fetching = async (data=null) => {
        try {
            setIsLoading(true);
            await callback(data);
        } catch (e) {
            setError(e.request);
        } finally {
            setIsLoading(false);
        }
    }
    return [fetching, isLoading, error]
}

export default useFetching;
