import API from './client';

export const auth = {
  login: d => API.post('/auth/login/', d),
  logout: () => API.post('/auth/logout/'),
  me: () => API.get('/auth/me/'),
};
export const profileAPI = {
  update: d => API.patch('/profile/update/', d),
  changePw: d => API.post('/profile/change-password/', d),
};
export const usersAPI = {
  list: p => API.get('/users/', { params: p }),
  create: d => API.post('/users/create/', d),
  delete: id => API.delete(`/users/${id}/delete/`),
  faculty: () => API.get('/faculty/'),
};
export const studentsAPI = {
  list: p => API.get('/students/', { params: p }),
  search: q => API.get('/students/search/', { params: { q } }),
};
export const csvAPI = {
  uploadStudents: (file, name) => { const fd = new FormData(); fd.append('file', file); if (name) fd.append('name', name); return API.post('/csv/upload/students/', fd); },
  uploadHalls: (file, name) => { const fd = new FormData(); fd.append('file', file); if (name) fd.append('name', name); return API.post('/csv/upload/halls/', fd); },
  uploadCombined: (file, name) => { const fd = new FormData(); fd.append('file', file); if (name) fd.append('name', name); return API.post('/csv/upload/combined/', fd); },
  list: p => API.get('/csv/', { params: p }),
  students: (id, p) => API.get(`/csv/${id}/students/`, { params: p }),
  halls: id => API.get(`/csv/${id}/halls/`),
  delete: id => API.delete(`/csv/${id}/delete/`),
};
export const sessionsAPI = {
  create: d => API.post('/sessions/create/', d),
  complete: id => API.post(`/sessions/${id}/complete/`),
  list: () => API.get('/sessions/'),
  detail: id => API.get(`/sessions/${id}/`),
  delete: id => API.delete(`/sessions/${id}/delete/`),
  hallLayout: (sid, hpk) => API.get(`/sessions/${sid}/hall-layout/${hpk}/`),
};
export const exportsAPI = {
  csv: id => API.get(`/export/csv/${id}/`, { responseType: 'blob' }),
  pdf: id => API.get(`/export/pdf/${id}/`, { responseType: 'blob' }),
};
export const dashboardAPI = { get: () => API.get('/dashboard/') };
export const studentAPI = {
  myAllocs: () => API.get('/my-allocations/'),
  hallLayout: (sid, hpk) => API.get(`/my-allocations/${sid}/hall/${hpk}/`),
};