import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import axios from 'axios';


//const getCookie = (name) => {
//    const value = `; ${document.cookie}`;
//    const parts = value.split(`; ${name}=`);
//    if (parts.length === 2) return parts.pop().split(';').shift();
//}
//
//axios.defaults.headers.post['X-CSRFToken'] = getCookie('csrftoken');
axios.defaults.withCredentials = true;
axios.defaults.headers['Authorization'] = localStorage.getItem('Authorization');


const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
    <App />,
);
