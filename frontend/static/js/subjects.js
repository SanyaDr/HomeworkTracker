let subjects = [];
let subjectToDelete = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadSubjects();
    setupEventListeners();
});

// Загрузка предметов
async function loadSubjects() {
    try {
        showLoading();

        subjects = await API.request('/subjects');

        if (subjects && subjects.length > 0) {
            renderSubjects(subjects);
            document.getElementById('emptyState').classList.add('d-none');
        } else {
            document.getElementById('subjectsContainer').innerHTML = '';
            document.getElementById('emptyState').classList.remove('d-none');
        }
    } catch (error) {
        console.error('Ошибка загрузки предметов:', error);
        showNotification('Не удалось загрузить предметы', 'danger');
    } finally {
        hideLoading();
    }
}

// Отображение предметов
async function renderSubjects(subjectsList) {
    const container = document.getElementById('subjectsContainer');

    if (!subjectsList || subjectsList.length === 0) {
        container.innerHTML = '';
        document.getElementById('emptyState').classList.remove('d-none');
        return;
    }

    let html = '';
    const tempColor = "#FF5733";
    const stats = await getSubjectStats();

    subjectsList.forEach(subject => {
        // Получаем статистику по предмету
        const subjectStats = stats.subject_stats.find(s => s.subject_id === subject.id);

        // if (!subjectStats) return; // Если статистики нет, пропускаем

        html += `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card subject-card h-100" style="border-left-color: ${subject.color || tempColor}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                    <h5 class="card-title mb-1">
                                        <span class="subject-dot me-2" 
                                              style="background-color: ${subject.color || tempColor}"></span>
                                        ${escapeHtml(subject.name)}
                                    </h5>
                                    <small class="text-muted">
                                        Добавлен: ${formatDate(new Date(subject.created_at))}
                                    </small>
                                </div>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary" type="button" 
                                            data-bs-toggle="dropdown">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <button class="dropdown-item edit-subject-btn" 
                                                    data-subject-id="${subject.id}">
                                                <i class="fas fa-edit me-2"></i>Изменить цвет
                                            </button>
                                        </li>
                                        <li>
                                            <button class="dropdown-item text-danger delete-subject-btn" 
                                                    data-subject-id="${subject.id}">
                                                <i class="fas fa-trash me-2"></i>Удалить
                                            </button>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="subject-stats">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Всего заданий:</span>
                                    <span class="fw-bold">${subjectStats.total_tasks}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Выполнено:</span>
                                    <span class="text-success fw-bold">${subjectStats.completed_tasks}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>В процессе:</span>
                                    <!-- <span class="text-warning fw-bold">${subjectStats.total_tasks - subjectStats.completed_tasks}</span> -->
                                    <span class="text-warning fw-bold">${subjectStats.inProcess_tasks}</span>
                                </div>
                            </div>
                            
                            <div class="mt-3 pt-3 border-top">
                                <a href="/tasks?subject_id=${subject.id}"
                                   class="btn btn-sm btn-outline-primary w-100">
                                    <i class="fas fa-tasks me-2"></i>Смотреть задания
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
    });

    container.innerHTML = html;
    attachSubjectEventListeners();
}

function getSubjectStats(){
    return API.request('/users/stats')
}

// Настройка событий
function setupEventListeners() {
    // Форма добавления предмета
    const addForm = document.getElementById('addSubjectForm');
    if (addForm) {
        addForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const subjectData = {
                name: document.getElementById('subjectName').value.trim(),
                color: document.getElementById('subjectColor').value
            };

            try {
                await API.request('/subjects', 'POST', subjectData);
                showNotification('Предмет успешно добавлен', 'success');

                // Закрываем модальное окно и очищаем форму
                const modal = bootstrap.Modal.getInstance(document.getElementById('addSubjectModal'));
                modal.hide();
                addForm.reset();
                document.getElementById('colorPreview').style.backgroundColor = '#3B82F6';

                // Перезагружаем список
                await loadSubjects();

            } catch (error) {
                showNotification(`Ошибка при добавлении предмета: ${error.message}`, 'danger');
            }
        });
    }

    // Палитра цветов
    document.querySelectorAll('.palette-color').forEach(color => {
        color.addEventListener('click', function() {
            const colorValue = this.dataset.color;
            document.getElementById('subjectColor').value = colorValue;
            document.getElementById('colorPreview').style.backgroundColor = colorValue;

            // Подсветка выбранного цвета
            document.querySelectorAll('.palette-color').forEach(c => {
                c.classList.remove('selected');
            });
            this.classList.add('selected');
        });
    });

    // Просмотр цвета
    const colorPreview = document.getElementById('colorPreview');
    const colorInput = document.getElementById('subjectColor');

    if (colorPreview && colorInput) {
        colorPreview.addEventListener('click', () => colorInput.click());
        colorInput.addEventListener('input', function() {
            colorPreview.style.backgroundColor = this.value;
        });
    }

    // Удаление предмета
    document.getElementById('confirmDeleteSubject')?.addEventListener('click', async function() {
        if (!subjectToDelete) return;

        try {
            await API.request(`/subjects/${subjectToDelete}`, 'DELETE');
            showNotification('Предмет успешно удален', 'success');
            await loadSubjects();
        } catch (error) {
            showNotification('Ошибка при удалении предмета', 'danger');
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteSubjectModal'));
        modal.hide();
        subjectToDelete = null;
    });
}

function attachSubjectEventListeners() {
    // Кнопки удаления
    document.querySelectorAll('.delete-subject-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            subjectToDelete = this.dataset.subjectId;
            const modal = new bootstrap.Modal(document.getElementById('deleteSubjectModal'));
            modal.show();
        });
    });

    // Кнопки редактирования (упрощенная версия)
    document.querySelectorAll('.edit-subject-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const subjectId = this.dataset.subjectId;
            const subject = subjects.find(s => s.id == subjectId);

            if (subject) {
                const newColor = prompt('Введите новый цвет в формате #RRGGBB:', subject.color);
                if (newColor && /^#[0-9A-F]{6}$/i.test(newColor)) {
                    updateSubjectColor(subjectId, newColor);
                } else if (newColor) {
                    showNotification('Неверный формат цвета. Используйте формат #RRGGBB', 'warning');
                }
            }
        });
    });
}

// Обновление цвета предмета
async function updateSubjectColor(subjectId, color) {
    try {
        await API.request(`/subjects/${subjectId}`, 'PATCH', { color });
        showNotification('Цвет предмета обновлен', 'success');
        await loadSubjects();
    } catch (error) {
        showNotification('Ошибка при обновлении цвета', 'danger');
    }
}

// Вспомогательные функции
function formatDate(date) {
    return date.toLocaleDateString('ru-RU');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading() {
    const container = document.getElementById('subjectsContainer');
    container.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-2 text-muted">Загружаем предметы...</p>
            </div>
        `;
}

function hideLoading() {
    // Контент уже заменится
}