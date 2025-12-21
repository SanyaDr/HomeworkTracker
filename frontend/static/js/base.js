// Легковесная проверка авторизации (без редиректов)
async function checkAuthLight() {
    try {
        const response = await fetch('/api/users/authStatus', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            return data.authenticated;
        }
        return false;
    } catch (error) {
        console.debug('Auth check failed:', error.message);
        return false;
    }
}

// Загрузка данных профиля (только для авторизованных)
async function loadUserProfile() {
    try {
        const response = await fetch('/api/users/authStatus', {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();

            if (data.authenticated && data.user) {
                // Обновляем UI
                const userName = document.getElementById('user-name');
                const userAvatar = document.getElementById('user-avatar');

                if (userName) userName.textContent = data.user.name;
                if (userAvatar) userAvatar.textContent = data.user.name.charAt(0).toUpperCase();

                // Сохраняем в localStorage для быстрого доступа
                // localStorage.setItem('user_data', JSON.stringify(data.user));

                return data.user;
            }
        }
    } catch (error) {
        console.debug('Не удалось загрузить статус авторизации:', error.message);
    }
    return null;
}

// API функции
const API = {
    baseURL: '/api',
    async request(endpoint, method = 'GET', data = null) {
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);

            // Обработка 401 ошибки
            if (response.status === 401) {
                console.log('Не авторизован, перенаправляю на логин...');
                window.location.href = '/login';
                return null;
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка сервера');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            // Не показываем уведомление для 401 ошибок
            if (!error.message.includes('401')) {
                showNotification(error.message, 'danger');
            }
            throw error;
        }
    },

    async login(username, password) {
        // Для входа используем FormData
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/api/users/login', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Неверный логин или пароль');
        }

        const data = await response.json();
        // Сохраняем токен в localStorage для быстрой проверки
        localStorage.setItem('access_token', data.access_token);
        return data;
    },

    async logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        await fetch('/api/users/logout', {
            method: 'POST',
            credentials: 'include'
        });
    },

    async getProfile() {
        return await this.request('/users/profile', 'GET');
    },
};

async function checkAuthFromCookie() {
    try {
        const response = await fetch('/api/users/authStatus', {
            method: 'GET',
            credentials: 'include'  // отправляем куки
        });

        const data = await response.json();
        return data.authenticated;
    } catch (error) {
        console.log('Ошибка проверки авторизации:', error);
        return false;
    }
}

// Использование:
document.addEventListener('DOMContentLoaded', async function() {
    const isAuth = await checkAuthFromCookie();

    if (isAuth) {
        // Показать меню для авторизованных
        document.getElementById('user-nav').style.display = 'flex';
        document.getElementById('guest-nav').style.display = 'none';
    } else {
        // Показать меню для гостей
        document.getElementById('user-nav').style.display = 'none';
        document.getElementById('guest-nav').style.display = 'flex';
    }
});

// Уведомления
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

    const container = document.querySelector('.container') || document.body;
    container.prepend(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async function() {
    // На главной и страницах логина/регистрации не проверяем
    const publicPages = ['/', '/login', '/register', '/forgot-password', '/reset-password', '/about'];
    const currentPath = window.location.pathname;

    // Всегда показываем гостевую навигацию по умолчанию
    const guestNav = document.getElementById('guest-nav');
    const userNav = document.getElementById('user-nav');

    if (guestNav) guestNav.style.display = 'none';
    if (userNav) userNav.style.display = 'none';
    const isAuth = await checkAuthLight();

    if (publicPages.includes(currentPath)) {
        // Для публичных страниц показываем гостевую навигацию
        if (guestNav) guestNav.style.display = 'flex';

        // Но все равно проверяем - может пользователь уже авторизован
        try {
            if (isAuth) {
                // Если авторизован на публичной странице - показываем пользовательскую навигацию
                if (userNav) userNav.style.display = 'flex';
                if (guestNav) guestNav.style.display = 'none';
                if (guestNav) guestNav.style.display = 'none';
                await loadUserProfile();
            }
        } catch (error) {
            // Игнорируем ошибки проверки на публичных страницах
        }
    } else {
        // Для защищенных страниц проверяем авторизацию
        if (isAuth) {
            if (userNav) userNav.style.display = 'flex';
            await loadUserProfile();
        } else {
            // Если не авторизован на защищенной странице - показываем гостевую
            if (guestNav) guestNav.style.display = 'flex';
        }
    }

    // Обработчик выхода
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            await API.logout();
            window.location.href = '/';
        });
    }

    // Проверяем кэшированные данные пользователя
    const cachedUser = localStorage.getItem('user_data');
    if (cachedUser) {
        try {
            const user = JSON.parse(cachedUser);
            const userName = document.getElementById('user-name');
            const userAvatar = document.getElementById('user-avatar');

            if (userName) userName.textContent = user.name;
            if (userAvatar) userAvatar.textContent = user.name.charAt(0).toUpperCase();
        } catch (error) {
            console.debug('Ошибка парсинга кэшированных данных пользователя');
        }
    }
});
