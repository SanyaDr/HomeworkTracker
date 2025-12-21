document.addEventListener('DOMContentLoaded', function() {
    // Переключатели видимости паролей
    const toggleNewPassword = document.getElementById('toggleNewPassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');

    if (toggleNewPassword) {
        toggleNewPassword.addEventListener('click', function() {
            const type = newPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            newPasswordInput.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }

    if (toggleConfirmPassword) {
        toggleConfirmPassword.addEventListener('click', function() {
            const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPasswordInput.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }

    // Проверка совпадения паролей
    function checkPasswordMatch() {
        const password = newPasswordInput.value;
        const confirm = confirmPasswordInput.value;
        const errorElement = document.getElementById('confirmPasswordError');

        if (confirm && password !== confirm) {
            errorElement.style.display = 'block';
            confirmPasswordInput.classList.add('is-invalid');
            return false;
        } else {
            errorElement.style.display = 'none';
            confirmPasswordInput.classList.remove('is-invalid');
            return true;
        }
    }

    // Слушатели для проверки паролей
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', checkPasswordMatch);
    }
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }

    // Обработка формы сброса пароля
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    const resetError = document.getElementById('resetError');
    const resetSuccess = document.getElementById('resetSuccess');

    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Сбрасываем ошибки
            resetError.classList.add('d-none');
            resetSuccess.classList.add('d-none');

            // Получаем данные
            const token = document.getElementById('resetToken').value;
            const newPassword = newPasswordInput.value;
            const confirmPassword = confirmPasswordInput.value;

            // Валидация
            if (!checkPasswordMatch()) {
                resetError.textContent = 'Пароли не совпадают';
                resetError.classList.remove('d-none');
                return;
            }

            if (newPassword.length < 8) {
                resetError.textContent = 'Пароль должен быть не менее 8 символов';
                resetError.classList.remove('d-none');
                return;
            }

            if (!token) {
                resetError.textContent = 'Неверная ссылка для сброса пароля';
                resetError.classList.remove('d-none');
                return;
            }

            // Показываем индикатор загрузки
            const submitBtn = resetPasswordForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Сохранение...';
            submitBtn.disabled = true;

            try {
                // Отправляем запрос на сброс пароля
                const response = await fetch('/api/users/reset-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token: token,
                        new_password: newPassword,
                        confirm_password: confirmPassword
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Показываем успешное сообщение
                    resetSuccess.innerHTML = `
                            <i class="fas fa-check-circle me-2"></i>
                            <strong>${data.message}</strong>
                            <br>
                            <small class="text-muted">Вы будете перенаправлены на страницу входа через 5 секунд...</small>
                        `;
                    resetSuccess.classList.remove('d-none');

                    // Перенаправляем на страницу входа через 5 секунд
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 5000);

                } else {
                    // Показываем ошибку от сервера
                    resetError.textContent = data.detail || 'Ошибка при сбросе пароля';
                    resetError.classList.remove('d-none');
                }

            } catch (error) {
                resetError.textContent = 'Ошибка соединения с сервером';
                resetError.classList.remove('d-none');
                console.error('Reset password error:', error);

            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Получаем токен из URL
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');

    if (tokenFromUrl && document.getElementById('resetToken')) {
        document.getElementById('resetToken').value = tokenFromUrl;
    } else if (!document.getElementById('resetToken').value) {
        // Если нет токена, показываем ошибку
        resetError.textContent = 'Неверная или устаревшая ссылка для сброса пароля';
        resetError.classList.remove('d-none');
    }
});