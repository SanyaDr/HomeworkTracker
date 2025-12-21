document.addEventListener('DOMContentLoaded', function() {
    // Переключатель видимости пароля
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }

    // Обработка формы входа
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Сбрасываем ошибки
            loginError.classList.add('d-none');
            loginError.textContent = '';

            // Получаем данные формы
            const login = document.getElementById('login').value.trim();
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;

            // Валидация
            if (!login || !password) {
                loginError.textContent = 'Пожалуйста, заполните все поля';
                loginError.classList.remove('d-none');
                return;
            }

            // Показываем индикатор загрузки
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Вход...';
            submitBtn.disabled = true;

            try {
                // Отправляем запрос на сервер
                const response = await API.login(login, password);

                // Сохраняем токен
                localStorage.setItem('access_token', response.access_token);

                // Если выбрано "Запомнить меня"
                if (rememberMe) {
                    localStorage.setItem('remember_me', 'true');
                }

                // Перенаправляем на дашборд
                window.location.href = '/dashboard';

            } catch (error) {
                // Показываем ошибку
                loginError.textContent = error.message || 'Ошибка при входе. Проверьте логин и пароль.';
                loginError.classList.remove('d-none');

                // Восстанавливаем кнопку
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;

                // Анимация ошибки
                loginForm.classList.add('shake');
                setTimeout(() => {
                    loginForm.classList.remove('shake');
                }, 500);
            }
        });
    }

    // Анимация тряски для формы
    const style = document.createElement('style');
    style.textContent = `
            .shake {
                animation: shake 0.5s ease-in-out;
            }
            
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
        `;
    document.head.appendChild(style);

    // Проверяем сохраненный логин
    const savedLogin = localStorage.getItem('saved_login');
    if (savedLogin && document.getElementById('login')) {
        document.getElementById('login').value = savedLogin;
        document.getElementById('rememberMe').checked = true;
        document.getElementById('password').focus();
    }

    // Автофокус на поле логина
    if (document.getElementById('login')) {
        document.getElementById('login').focus();
    }
});