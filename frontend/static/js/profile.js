let userData = null;
let userStats = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadProfileData();
    setupEventListeners();
    // loadSampleData(); // Для демонстрации, пока нет реальных данных
});

// Загрузка данных профиля
async function loadProfileData() {
    try {
        // Загружаем профиль пользователя
        userData = await API.getProfile();

        if (userData) {
            updateProfileUI(userData);

            // Загружаем статистику
            await loadUserStats();

            // Загружаем активность
            await loadUserActivity();
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
        showNotification('Не удалось загрузить данные профиля', 'danger');
    }
}

// Обновление UI профиля
function updateProfileUI(user) {
    // Основная информация
    document.getElementById('profileName').textContent = user.name;
    document.getElementById('profileEmail').textContent = user.email;
    document.getElementById('profileLogin').textContent = user.login;
    document.getElementById('profileDisplayName').textContent = user.name;
    document.getElementById('profileDisplayEmail').textContent = user.email;
    document.getElementById('profileGroup').textContent = user.groupName || 'Не указано';
    document.getElementById('profileCreatedAt').textContent = formatDate(new Date(user.created_at));
    document.getElementById('profileStatus').textContent = user.is_active ? 'Активен' : 'Неактивен';

    // Аватар (первая буква имени)
    const avatar = document.getElementById('profileAvatar');
    if (avatar) {
        const firstLetter = user.name.charAt(0).toUpperCase();
        avatar.textContent = firstLetter;
        avatar.style.backgroundColor = stringToColor(user.name);
    }
}

// Загрузка статистики
async function loadUserStats() {
    try {
        userStats = await API.request('/users/stats');

        if (userStats.overview.total_tasks !== 0){
            userStats.productivity_score = (userStats.overview.completed_tasks / userStats.overview.total_tasks) * 100;
        }
        if (userStats) {
            document.getElementById('total_tasks').textContent = userStats.overview.total_tasks || 0;
            document.getElementById('completed_tasks').textContent = userStats.overview.completed_tasks || 0;
            document.getElementById('total_subjects').textContent = userStats.subject_stats.length || 0;
            updateDetailedStats(userStats);
        }

    } catch (error) {
        console.log('Ошибка загрузки данных', error);
        userStats = {
            total_tasks: 0,
            completed_tasks: 0,
            total_subjects: 0,
            productivity_score: 0,
            streak_days: 0,
            avg_completion_time: '0 дней'
        };
        updateDetailedStats(userStats);
    }
}

// Обновление детальной статистики
function updateDetailedStats(stats) {
    const container = document.getElementById('detailedStats');
    container.innerHTML = `
            <div class="col-md-4 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-3 fw-bold text-primary">${stats.productivity_score || 0}%</div>
                    <small class="text-muted">Продуктивность</small>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-3 fw-bold text-success">${stats.streak_days || 1}</div>
                    <small class="text-muted">Дней подряд</small>
                </div>
            </div>
            <!--
            <div class="col-md-4 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-3 fw-bold text-info">${stats.avg_completion_time || '0 дней'}</div>
                    <small class="text-muted">Среднее время выполнения</small>
                </div>
            </div> -->
        `;
}

// Загрузка активности
async function loadUserActivity() {
    const container = document.getElementById('recentActivity');

    // Демо-данные активности
    const activities = [
        { icon: 'fas fa-plus', color: 'success', text: 'Добавлено новое задание "Лабораторная работа"', time: '2 часа назад' },
        { icon: 'fas fa-check', color: 'primary', text: 'Задание "Домашняя работа" выполнено', time: 'Вчера, 14:30' },
        { icon: 'fas fa-book', color: 'info', text: 'Добавлен новый предмет "Физика"', time: '2 дня назад' },
        { icon: 'fas fa-user', color: 'warning', text: 'Обновлена информация профиля', time: '3 дня назад' },
        { icon: 'fas fa-sign-in-alt', color: 'secondary', text: 'Выполнен вход в аккаунт', time: 'Неделю назад' }
    ];

    let html = '';
    activities.forEach(activity => {
        html += `
                <div class="activity-item">
                    <div class="d-flex">
                        <div class="activity-icon bg-${activity.color}-subtle text-${activity.color}">
                            <i class="${activity.icon}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <p class="mb-1">${activity.text}</p>
                            <small class="text-muted">${activity.time}</small>
                        </div>
                    </div>
                </div>
            `;
    });

    container.innerHTML = html;
}

// Настройка всех событий
function setupEventListeners() {
    // Кнопка редактирования профиля
    document.getElementById('editProfileBtn')?.addEventListener('click', function() {
        if (userData) {
            document.getElementById('editName').value = userData.name;
            document.getElementById('editEmail').value = userData.email;
            document.getElementById('editGroup').value = userData.groupName || '';

            const modal = new bootstrap.Modal(document.getElementById('editProfileModal'));
            modal.show();
        }
    });

    // Форма редактирования профиля
    const editProfileForm = document.getElementById('editProfileForm');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const updatedData = {
                name: document.getElementById('editName').value.trim(),
                email: document.getElementById('editEmail').value.trim(),
                groupName: document.getElementById('editGroup').value.trim() || null
            };

            try {
                const updatedUser = await API.request('/users', 'PUT', updatedData);

                showNotification('Профиль успешно обновлен', 'success');
                userData = updatedUser;
                updateProfileUI(userData);

                const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
                modal.hide();

            } catch (error) {
                document.getElementById('editProfileError').textContent = error.message;
                document.getElementById('editProfileError').classList.remove('d-none');
            }
        });
    }

    // Форма смены пароля
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // Валидация
            if (newPassword !== confirmPassword) {
                document.getElementById('passwordError').textContent = 'Пароли не совпадают';
                document.getElementById('passwordError').classList.remove('d-none');
                return;
            }

            if (newPassword.length < 8) {
                document.getElementById('passwordError').textContent = 'Пароль должен содержать минимум 8 символов';
                document.getElementById('passwordError').classList.remove('d-none');
                return;
            }

            try {
                await API.request('/users/profile/changePassword', 'POST', {
                    old_password: currentPassword,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                });

                document.getElementById('passwordSuccess').textContent = 'Пароль успешно изменен';
                document.getElementById('passwordSuccess').classList.remove('d-none');
                document.getElementById('passwordError').classList.add('d-none');

                changePasswordForm.reset();

                // Через 3 секунды скрываем сообщение
                setTimeout(() => {
                    document.getElementById('passwordSuccess').classList.add('d-none');
                }, 3000);

            } catch (error) {
                document.getElementById('passwordError').textContent = error.message;
                document.getElementById('passwordError').classList.remove('d-none');
            }
        });
    }

    // Кнопки показа/скрытия пароля
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    });

    // Сохранение настроек
    document.getElementById('saveSettings')?.addEventListener('click', async function() {
        const settings = {
            notifications: {
                email: document.getElementById('emailNotifications').checked,
                deadlines: document.getElementById('deadlineReminders').checked,
                weekly: document.getElementById('weeklyReports').checked
            },
            appearance: {
                theme: document.getElementById('themeSelect').value,
                density: document.getElementById('densitySelect').value,
                language: document.getElementById('languageSelect').value
            },
            dashboard: {
                widgets: {
                    tasks: document.getElementById('widgetTasks').checked,
                    calendar: document.getElementById('widgetCalendar').checked,
                    stats: document.getElementById('widgetStats').checked,
                    recent: document.getElementById('widgetRecent').checked
                }
            }
        };

        try {
            await API.request('/users/settings', 'PUT', settings);
            showNotification('Настройки сохранены', 'success');
        } catch (error) {
            showNotification('Ошибка сохранения настроек', 'danger');
        }
    });

    // Сброс настроек
    document.getElementById('resetSettings')?.addEventListener('click', function() {
        if (confirm('Сбросить все настройки к значениям по умолчанию?')) {
            resetSettingsToDefault();
            showNotification('Настройки сброшены', 'info');
        }
    });

    // Подтверждение удаления аккаунта
    const confirmDeleteText = document.getElementById('confirmDeleteText');
    const confirmDeleteAccount = document.getElementById('confirmDeleteAccount');

    if (confirmDeleteText && confirmDeleteAccount) {
        confirmDeleteText.addEventListener('input', function() {
            confirmDeleteAccount.disabled = this.value !== 'УДАЛИТЬ АККАУНТ';
        });

        confirmDeleteAccount.addEventListener('click', async function() {
            if (confirm('Вы точно хотите удалить аккаунт? Это действие нельзя отменить.')) {
                try {
                    await API.request('/users/profile', 'DELETE');
                    showNotification('Аккаунт удален', 'success');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } catch (error) {
                    showNotification('Ошибка удаления аккаунта', 'danger');
                }
            }
        });
    }

    // Подтверждение удаления данных
    const confirmDataText = document.getElementById('confirmDataText');
    const confirmDeleteData = document.getElementById('confirmDeleteData');

    if (confirmDataText && confirmDeleteData) {
        confirmDataText.addEventListener('input', function() {
            confirmDeleteData.disabled = this.value !== 'УДАЛИТЬ ДАННЫЕ';
        });

        confirmDeleteData.addEventListener('click', async function() {
            if (confirm('Вы точно хотите удалить все данные? Это действие нельзя отменить.')) {
                try {
                    await API.request('/users/data', 'DELETE');
                    showNotification('Все данные удалены', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } catch (error) {
                    showNotification('Ошибка удаления данных', 'danger');
                }
            }
        });
    }

    // Экспорт данных
    document.getElementById('exportJSON')?.addEventListener('click', () => exportData('json'));
    document.getElementById('exportCSV')?.addEventListener('click', () => exportData('csv'));
    document.getElementById('exportPDF')?.addEventListener('click', () => exportData('pdf'));
}

// Сброс настроек к значениям по умолчанию
function resetSettingsToDefault() {
    document.getElementById('emailNotifications').checked = true;
    document.getElementById('deadlineReminders').checked = true;
    document.getElementById('weeklyReports').checked = false;

    document.getElementById('themeSelect').value = 'light';
    document.getElementById('densitySelect').value = 'normal';
    document.getElementById('languageSelect').value = 'ru';

    document.getElementById('widgetTasks').checked = true;
    document.getElementById('widgetCalendar').checked = true;
    document.getElementById('widgetStats').checked = true;
    document.getElementById('widgetRecent').checked = false;
}

// // Экспорт данных
// async function exportData(format) {
//     try {
//         const data = await API.request(`/users/export/${format}`);
//
//         if (format === 'json') {
//             downloadFile(JSON.stringify(data, null, 2), `profile_${Date.now()}.json`, 'application/json');
//         } else if (format === 'csv') {
//             downloadFile(data, `profile_${Date.now()}.csv`, 'text/csv');
//         } else if (format === 'pdf') {
//             // Для PDF обычно сервер возвращает бинарные данные
//             showNotification('PDF отчет готовится...', 'info');
//         }
//
//         showNotification(`Данные экспортированы в формате ${format.toUpperCase()}`, 'success');
//     } catch (error) {
//         showNotification('Ошибка экспорта данных', 'danger');
//     }
// }
//
// // Вспомогательная функция для скачивания файла
// function downloadFile(content, filename, contentType) {
//     const blob = new Blob([content], { type: contentType });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = filename;
//     document.body.appendChild(a);
//     a.click();
//     document.body.removeChild(a);
//     URL.revokeObjectURL(url);
// }

// Генерация цвета из строки
function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 60%)`;
}

// Форматирование даты
function formatDate(date) {
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Загрузка демо-данных (временная функция)
function loadSampleData() {
    // Активные сессии
    const sessionsContainer = document.getElementById('activeSessions');
    if (sessionsContainer) {
        sessionsContainer.innerHTML = `
                <div class="card session-card session-current mb-2">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">Текущее устройство</h6>
                                <small class="text-muted">
                                    <i class="fas fa-laptop me-1"></i>Windows • Chrome • Москва
                                </small>
                            </div>
                            <span class="badge bg-primary">Сейчас</span>
                        </div>
                    </div>
                </div>
                <div class="card session-card mb-2">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">iPhone 13</h6>
                                <small class="text-muted">
                                    <i class="fas fa-mobile-alt me-1"></i>Safari • 2 дня назад
                                </small>
                            </div>
                            <button class="btn btn-sm btn-outline-danger">
                                <i class="fas fa-sign-out-alt"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
    }

    // Журнал безопасности
    const securityLog = document.getElementById('securityLog');
    if (securityLog) {
        const logs = [
            { action: 'Смена пароля', device: 'Chrome, Windows', time: 'Сегодня, 10:30' },
            { action: 'Вход в аккаунт', device: 'Safari, iPhone', time: 'Вчера, 14:20' },
            { action: 'Обновление профиля', device: 'Chrome, Windows', time: '3 дня назад' },
            { action: 'Добавлено новое устройство', device: 'Firefox, Linux', time: 'Неделю назад' }
        ];

        let html = '';
        logs.forEach(log => {
            html += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between">
                            <div>
                                <small class="fw-bold">${log.action}</small><br>
                                <small class="text-muted">${log.device}</small>
                            </div>
                            <small class="text-muted">${log.time}</small>
                        </div>
                    </div>
                `;
        });
        securityLog.innerHTML = html;
    }
}