import axios from 'axios';

// Функция для обновления токена
export async function refreshToken() {
  try {
    const response = await axios.post('http://127.0.0.1:8000/auth/refresh', {}, { withCredentials: true });
    localStorage.setItem('authToken', response.data.access_token);
  } catch (error) {
    console.error('Ошибка при обновлении токена', error);
  }
}

// Функция для проверки истечения токена
export function isTokenExpired(token) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));

  const decodedToken = JSON.parse(jsonPayload);
  const currentTime = Math.floor(Date.now() / 1000);
  return decodedToken.exp < currentTime;
}

// Функция для обновления токена, если он истёк
export async function checkAndRefreshToken() {
  const token = localStorage.getItem('authToken');
  if (isTokenExpired(token)) {
    await refreshToken();
  }
}