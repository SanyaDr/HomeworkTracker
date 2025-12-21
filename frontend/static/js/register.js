 document.addEventListener('DOMContentLoaded', function() {
    // Переключатели видимости паролей
    const toggleRegPassword = document.getElementById('toggleRegPassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const regPassword = document.getElementById('regPassword');
    const confirmPassword = document.getElementById('regConfirmPassword');

    if (toggleRegPassword) {
    toggleRegPassword.addEventListener('click', function() {
    const type = regPassword.getAttribute('type') === 'password' ? 'text' : 'password';
    regPassword.setAttribute('type', type);
    this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
});
}

    if (toggleConfirmPassword) {
    toggleConfirmPassword.addEventListener('click', function() {
    const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
    confirmPassword.setAttribute('type', type);
    this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
});
}

    // Проверка сложности пароля
    function checkPasswordStrength(password) {
    let strength = 0;
    const strengthBar = document.getElementById('passwordStrength');
    const strengthHint = document.getElementById('passwordHint');

    if (!password) {
    strengthBar.style.width = '0%';
    strengthBar.className = 'progress-bar';
    strengthHint.textContent = 'Введите пароль';
    return;
}

    // Длина пароля
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;

    // Наличие разных типов символов
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    // Обновляем индикатор
    const percentage = Math.min((strength / 6) * 100, 100);
    strengthBar.style.width = percentage + '%';

    // Цвет и текст в зависимости от силы
    if (strength < 2) {
    strengthBar.className = 'progress-bar bg-danger';
    strengthHint.textContent = 'Слабый пароль';
} else if (strength < 4) {
    strengthBar.className = 'progress-bar bg-warning';
    strengthHint.textContent = 'Средний пароль';
} else {
    strengthBar.className = 'progress-bar bg-success';
    strengthHint.textContent = 'Надежный пароль';
}
}

    // Проверка совпадения паролей
    function checkPasswordMatch() {
    const password = regPassword.value;
    const confirm = confirmPassword.value;
    const errorElement = document.getElementById('confirmPasswordError');

    if (confirm && password !== confirm) {
    errorElement.style.display = 'block';
    confirmPassword.classList.add('is-invalid');
    return false;
} else {
    errorElement.style.display = 'none';
    confirmPassword.classList.remove('is-invalid');
    return true;
}
}

    // Слушатели событий
    if (regPassword) {
    regPassword.addEventListener('input', function() {
    checkPasswordStrength(this.value);
    checkPasswordMatch();
});
}

    if (confirmPassword) {
    confirmPassword.addEventListener('input', checkPasswordMatch);
}

    // Обработка формы регистрации
    const registerForm = document.getElementById('registerForm');
    const registerError = document.getElementById('registerError');
    const registerSuccess = document.getElementById('registerSuccess');

    if (registerForm) {
    registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Сбрасываем ошибки
    registerError.classList.add('d-none');
    registerSuccess.classList.add('d-none');

    // Получаем данные формы
    const formData = {
    login: document.getElementById('regLogin').value.trim(),
    email: document.getElementById('regEmail').value.trim(),
    name: document.getElementById('regName').value.trim(),
    groupName: document.getElementById('regGroup').value.trim() || null,
    password: document.getElementById('regPassword').value,
};

    // Валидация
    if (!checkPasswordMatch()) {
    registerError.textContent = 'Пароли не совпадают';
    registerError.classList.remove('d-none');
    return;
}

    if (formData.password.length < 6) {
    registerError.textContent = 'Пароль должен быть не менее 6 символов';
    registerError.classList.remove('d-none');
    return;
}

    if (!document.getElementById('agreeTerms').checked) {
    registerError.textContent = 'Вы должны согласиться с условиями использования';
    registerError.classList.remove('d-none');
    return;
}

    // Показываем индикатор загрузки
    const submitBtn = registerForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Регистрация...';
    submitBtn.disabled = true;


    try {
    // Отправляем запрос на сервер
    console.log("Начал обработку")
    const response = await API.request('/users/register', 'POST', formData);
    // Показываем успех
    registerSuccess.innerHTML = `
                        <i class="fas fa-check-circle me-2"></i>
                        Аккаунт успешно создан! Перенаправляем на страницу входа...
                    `;
    registerSuccess.classList.remove('d-none');
    console.log("Закончил обработку")

    // Автоматический вход через 2 секунды
    setTimeout(async () => {
    try {
    const loginResponse = await API.login(formData.login, formData.password);
    localStorage.setItem('access_token', loginResponse.access_token);
    window.location.href = '/dashboard';
} catch (loginError) {
    // Если автовход не удался, идем на страницу входа
    window.location.href = '/login';
}
}, 2000);

} catch (error) {
    console.log(error)
    // Показываем ошибку
    registerError.textContent = error.message || 'Ошибка при регистрации. Попробуйте еще раз.';
    registerError.classList.remove('d-none');

    // Восстанавливаем кнопку
    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;

    // Прокручиваем к ошибке
    registerError.scrollIntoView({ behavior: 'smooth' });
}
});
}

    // Автофокус на поле логина
    if (document.getElementById('regLogin')) {
    document.getElementById('regLogin').focus();
}
});
