import axios from 'axios';
const API = axios.create({ baseURL: '/api', withCredentials: true });
API.interceptors.request.use((c) => {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  if (m) c.headers['X-CSRFToken'] = m[1];
  if (c.data instanceof FormData) delete c.headers['Content-Type'];
  return c;
});
export default API;