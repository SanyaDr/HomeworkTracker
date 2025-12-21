document.addEventListener('DOMContentLoaded', function() {
    // Обработка формы восстановления пароля
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const forgotError = document.getElementById('forgotError');
    const forgotSuccess = document.getElementById('forgotSuccess');

    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Сбрасываем ошибки
            forgotError.classList.add('d-none');
            forgotSuccess.classList.add('d-none');

            // Получаем email
            const email = document.getElementById('email').value.trim();

            // Валидация
            if (!email) {
                forgotError.textContent = 'Пожалуйста, введите email';
                forgotError.classList.remove('d-none');
                return;
            }

            // Простая валидация email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                forgotError.textContent = 'Пожалуйста, введите корректный email';
                forgotError.classList.remove('d-none');
                return;
            }

            // Показываем индикатор загрузки
            const submitBtn = forgotPasswordForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Отправка...';
            submitBtn.disabled = true;

            try {
                // Отправляем запрос на сервер для проверки email
                const response = await fetch('/api/users/forgot-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: email })
                });

                const data = await response.json();

                if (response.ok) {
                    // Показываем успешное сообщение
                    forgotSuccess.innerHTML = `
                            <i class="fas fa-check-circle me-2"></i>
                            <strong>${data.message}</strong>
                            ${data.debug_url ? `<br><small class="text-muted mt-2 d-block">Ссылка для разработки: ${data.debug_url}</small>` : ''}
                        `;
                    forgotSuccess.classList.remove('d-none');

                    // Очищаем поле
                    document.getElementById('email').value = '';

                    // Скрываем сообщение через 10 секунд
                    setTimeout(() => {
                        forgotSuccess.classList.add('d-none');
                    }, 10000);

                } else {
                    // Показываем ошибку от сервера
                    forgotError.textContent = data.detail || 'Ошибка при отправке запроса';
                    forgotError.classList.remove('d-none');
                }

            } catch (error) {
                // Показываем ошибку сети
                forgotError.textContent = 'Ошибка соединения с сервером. Проверьте интернет-соединение.';
                forgotError.classList.remove('d-none');
                console.error('Forgot password error:', error);

            } finally {
                // Восстанавливаем кнопку
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Автофокус на поле email
    if (document.getElementById('email')) {
        document.getElementById('email').focus();
    }
});