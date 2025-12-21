let currentTasks = [];
let currentSubjects = [];
let currentFilter = 'all';
let currentPage = 1;
const tasksPerPage = 10;
let taskToDelete = null;

document.addEventListener('DOMContentLoaded', async function() {
    await Promise.all([loadTasks(), loadSubjects()]);
    setupEventListeners();
});

// Загрузка заданий
async function loadTasks() {
    try {
        showLoading();

        const response = await API.request('/tasks');
        if (response && response.tasks) {
            currentTasks = response.tasks;
            updateStats(currentTasks);
            renderTasks(currentTasks);
            setupPagination(currentTasks.length);
        }
    } catch (error) {
        console.error('Ошибка загрузки заданий:', error);
        showNotification('Не удалось загрузить задания', 'danger');
    } finally {
        hideLoading();
    }
}

// Загрузка предметов
async function loadSubjects() {
    try {
        const subjects = await API.request('/subjects');
        currentSubjects = subjects || [];

        populateSubjectSelect(currentSubjects);
        populateQuickSubjects(currentSubjects);
        populateModalQuickSubjects(currentSubjects);

        // Показываем блок быстрого выбора, если есть предметы
        const quickSubjectsCard = document.getElementById('quickSubjectsCard');
        if (quickSubjectsCard && currentSubjects.length > 0) {
            quickSubjectsCard.classList.remove('d-none');
        }

    } catch (error) {
        console.error('Ошибка загрузки предметов:', error);
    }
}

// Обновление статистики
function updateStats(tasks) {
    const statsContainer = document.getElementById('statsContainer');

    const stats = {
        total: tasks.length,
        completed: tasks.filter(t => t.status === 'completed').length,
        assigned: tasks.filter(t => t.status === 'assigned').length,
        overdue: tasks.filter(t => {
            if (!t.deadline || t.status === 'completed') return false;
            return new Date(t.deadline) < new Date();
        }).length
    };

    statsContainer.innerHTML = `
            <div class="col-md-3 col-6 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-4 fw-bold">${stats.total}</div>
                    <small class="text-muted">Всего</small>
                </div>
            </div>
            <div class="col-md-3 col-6 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-4 fw-bold text-success">${stats.completed}</div>
                    <small class="text-muted">Выполнено</small>
                </div>
            </div>
            <div class="col-md-3 col-6 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-4 fw-bold text-warning">${stats.assigned}</div>
                    <small class="text-muted">Текущие</small>
                </div>
            </div>
            <div class="col-md-3 col-6 mb-3">
                <div class="card text-center p-3">
                    <div class="fs-4 fw-bold text-danger">${stats.overdue}</div>
                    <small class="text-muted">Просрочено</small>
                </div>
            </div>
        `;
}

// Заполнение выпадающего списка предметов
function populateSubjectSelect(subjects) {
    const select = document.getElementById('taskSubject');
    select.innerHTML = '<option value="" selected disabled>Выберите предмет</option>';

    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.id;
        option.textContent = subject.name;
        option.style.color = subject.color;
        select.appendChild(option);
    });
}

// Заполнение быстрого выбора на странице
function populateQuickSubjects(subjects) {
    const container = document.getElementById('quickSubjectsContainer');
    container.innerHTML = '';

    subjects.slice(0, 8).forEach(subject => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm quick-subject';
        btn.style.backgroundColor = `${subject.color}15`; // 10% прозрачность
        btn.style.borderColor = subject.color;
        btn.style.color = subject.color;
        btn.innerHTML = `
                <span class="subject-dot" style="background-color: ${subject.color}"></span>
                ${subject.name}
            `;
        btn.onclick = () => {
            // Открываем модальное окно с уже выбранным предметом
            document.getElementById('taskSubject').value = subject.id;
            const modal = new bootstrap.Modal(document.getElementById('addTaskModal'));
            modal.show();
            document.getElementById('taskTitle').focus();
        };
        container.appendChild(btn);
    });
}

// Заполнение быстрого выбора в модальном окне
function populateModalQuickSubjects(subjects) {
    const container = document.getElementById('modalQuickSubjects');
    container.innerHTML = '';

    subjects.slice(0, 6).forEach(subject => {
        const colorDiv = document.createElement('div');
        colorDiv.className = 'palette-color';
        colorDiv.style.backgroundColor = subject.color;
        colorDiv.title = subject.name;
        colorDiv.dataset.subjectId = subject.id;
        colorDiv.onclick = () => {
            document.getElementById('taskSubject').value = subject.id;

            // Подсветка выбранного цвета
            container.querySelectorAll('.palette-color').forEach(c => {
                c.classList.remove('selected');
            });
            colorDiv.classList.add('selected');
        };
        container.appendChild(colorDiv);
    });
}

// Отображение заданий
function renderTasks(tasks) {
    const container = document.getElementById('tasksContainer');

    if (tasks.length === 0) {
        container.innerHTML = `
                <div class="empty-state">
                    <div class="mb-3">
                        <i class="fas fa-tasks fa-3x text-muted"></i>
                    </div>
                    <h5 class="mb-2">Заданий не найдено</h5>
                    <p class="text-muted mb-3">Попробуйте изменить фильтры или добавьте новое задание</p>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addTaskModal">
                        <i class="fas fa-plus me-2"></i>Добавить задание
                    </button>
                </div>
            `;
        return;
    }

    // Фильтрация и пагинация
    const filteredTasks = filterTasks(tasks);
    const startIndex = (currentPage - 1) * tasksPerPage;
    const paginatedTasks = filteredTasks.slice(startIndex, startIndex + tasksPerPage);

    let html = '';

    paginatedTasks.forEach(task => {
        const deadline = task.deadline ? new Date(task.deadline) : null;
        const isOverdue = deadline && deadline < new Date() && task.status !== 'completed';
        const priorityClass = getPriorityClass(task.priority);
        const statusClass = task.status === 'completed' ? 'completed' : '';

        html += `
                <div class="task-card card mb-3 ${statusClass} ${priorityClass}" data-task-id="${task.id}">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <!-- Название и описание -->
                            <div class="col-md-5 mb-2 mb-md-0">
                                <div class="d-flex align-items-start">
                                    <div class="form-check me-2">
                                        <input class="form-check-input task-checkbox" type="checkbox"
                                               ${task.status === 'completed' ? 'checked' : ''}
                                               data-task-id="${task.id}">
                                    </div>
                                    <div>
                                        <h6 class="mb-1">${escapeHtml(task.title)}</h6>
                                        ${task.description ?
            `<p class="text-muted small mb-0">${escapeHtml(task.description)}</p>` : ''}
                                    </div>
                                </div>
                            </div>

                            <!-- Предмет -->
                            <div class="col-md-2 mb-2 mb-md-0">
                                <div class="d-flex align-items-center">
                                    <span class="subject-color" style="background-color: ${task.subject_color || '#4361ee'}"></span>
                                    <span>${task.subject_name || 'Без предмета'}</span>
                                </div>
                            </div>

                            <!-- Приоритет -->
                            <div class="col-md-2 mb-2 mb-md-0">
                                <span class="priority-badge ${getPriorityBadgeClass(task.priority)}">
                                    ${getPriorityText(task.priority)}
                                </span>
                            </div>

                            <!-- Срок -->
                            <div class="col-md-2 mb-2 mb-md-0">
                                ${deadline ?
            `<span class="${isOverdue ? 'text-danger' : 'text-muted'}">
                                        <i class="far fa-calendar-alt me-1"></i>
                                        ${formatDate(deadline)}
                                        ${isOverdue ? '<i class="fas fa-exclamation-circle ms-1"></i>' : ''}
                                    </span>` :
            '<span class="text-muted">Нет срока</span>'
        }
                            </div>

                            <!-- Действия -->
                            <div class="col-md-1">
                                <div class="task-actions">
                                    <div class="dropdown">
                                        <button class="btn btn-sm btn-outline-secondary" type="button"
                                                data-bs-toggle="dropdown">
                                            <i class="fas fa-ellipsis-v"></i>
                                        </button>
                                        <ul class="dropdown-menu">
                                            <li>
                                                <a class="dropdown-item edit-task-btn" href="#" data-task-id="${task.id}">
                                                    <i class="fas fa-edit me-2"></i>Редактировать
                                                </a>
                                            </li>
                                            <li>
                                                <a class="dropdown-item text-danger delete-task-btn"
                                                   href="#" data-task-id="${task.id}">
                                                    <i class="fas fa-trash me-2"></i>Удалить
                                                </a>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
    });

    container.innerHTML = html;
    attachTaskEventListeners();
}

// Сброс формы задания
function resetTaskForm() {
    const form = document.getElementById('addTaskForm');
    form.reset();
    form.dataset.editMode = 'false';
    delete form.dataset.editTaskId;
    document.getElementById('hasDeadline').checked = false;
    document.getElementById('deadlineFields').style.display = 'none';
    document.getElementById('addTaskModalLabel').innerHTML =
        '<i class="fas fa-plus-circle me-2"></i>Добавить новое задание';
}

// Настройка всех событий
function setupEventListeners() {
    // Фильтры
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            currentPage = 1;
            renderTasks(currentTasks);
            updatePaginationInfo();
        });
    });

    // Поиск
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const filtered = currentTasks.filter(task =>
                task.title.toLowerCase().includes(searchTerm) ||
                (task.description && task.description.toLowerCase().includes(searchTerm))
            );
            renderTasks(filtered);
        });
    }

    // Форма добавления задания
    const addTaskForm = document.getElementById('addTaskForm');
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            if (!validateTaskForm()) {
                return;
            }

            const taskData = getTaskFormData();
            const isEditMode = this.dataset.editMode === 'true';
            const taskId = this.dataset.editTaskId;

            try {
                if (isEditMode) {
                    // Редактирование существующего задания
                    await API.request(`/tasks/${taskId}`, 'PUT', taskData);
                    showNotification('Задание успешно обновлено!', 'success');
                } else {
                    // Создание нового задания
                    await API.request('/tasks', 'POST', taskData);
                    showNotification('Задание успешно добавлено!', 'success');
                }

                // Закрываем модальное окно и очищаем форму
                const modal = bootstrap.Modal.getInstance(document.getElementById('addTaskModal'));
                modal.hide();
                resetTaskForm();

                // Перезагружаем задания
                await loadTasks();

            } catch (error) {
                showNotification(`Ошибка: ${error.message}`, 'danger');
            }
        });
    }

    // Форма добавления предмета
    const addSubjectForm = document.getElementById('addSubjectForm');
    if (addSubjectForm) {
        addSubjectForm.addEventListener('submit', async function(e) {
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
                addSubjectForm.reset();
                document.getElementById('colorPreview').style.backgroundColor = '#3B82F6';

                // Перезагружаем предметы
                await loadSubjects();

            } catch (error) {
                showNotification(`Ошибка при добавлении предмета: ${error.message}`, 'danger');
            }
        });
    }

    // Быстрый выбор приоритета
    document.querySelectorAll('.quick-priority').forEach(btn => {
        btn.addEventListener('click', function() {
            const priority = this.dataset.priority;
            document.getElementById('taskPriority').value = priority;

            // Подсветка активной кнопки
            document.querySelectorAll('.quick-priority').forEach(b => {
                b.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // Показать/скрыть поля срока
    const hasDeadlineCheckbox = document.getElementById('hasDeadline');
    const deadlineFields = document.getElementById('deadlineFields');

    if (hasDeadlineCheckbox && deadlineFields) {
        hasDeadlineCheckbox.addEventListener('change', function() {
            deadlineFields.style.display = this.checked ? 'block' : 'none';
            if (this.checked) {
                // Установить дату на завтра по умолчанию
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                document.getElementById('deadlineDate').valueAsDate = tomorrow;
            }
        });
    }

    // Палитра цветов для предметов
    const colorPreview = document.getElementById('colorPreview');
    const colorInput = document.getElementById('subjectColor');

    if (colorPreview && colorInput) {
        colorPreview.addEventListener('click', () => colorInput.click());
        colorInput.addEventListener('input', function() {
            colorPreview.style.backgroundColor = this.value;
        });
    }

    document.querySelectorAll('#addSubjectForm .palette-color').forEach(color => {
        color.addEventListener('click', function() {
            const colorValue = this.dataset.color;
            document.getElementById('subjectColor').value = colorValue;
            document.getElementById('colorPreview').style.backgroundColor = colorValue;

            // Подсветка выбранного цвета
            document.querySelectorAll('#addSubjectForm .palette-color').forEach(c => {
                c.classList.remove('selected');
            });
            this.classList.add('selected');
        });
    });

    // Удаление задания
    document.getElementById('confirmDeleteTask')?.addEventListener('click', async function() {
        if (!taskToDelete) return;

        try {
            await API.request(`/tasks/${taskToDelete}`, 'DELETE');
            showNotification('Задание успешно удалено', 'success');
            await loadTasks(); // Перезагружаем список
        } catch (error) {
            showNotification('Ошибка при удалении задания', 'danger');
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteTaskModal'));
        modal.hide();
        taskToDelete = null;
    });

    // Пагинация
    document.getElementById('prevPage')?.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTasks(currentTasks);
            updatePaginationInfo();
        }
    });

    document.getElementById('nextPage')?.addEventListener('click', () => {
        const filteredTasks = filterTasks(currentTasks);
        const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);

        if (currentPage < totalPages) {
            currentPage++;
            renderTasks(currentTasks);
            updatePaginationInfo();
        }
    });

    // Сброс формы при закрытии модального окна
    const addTaskModal = document.getElementById('addTaskModal');
    if (addTaskModal) {
        addTaskModal.addEventListener('hidden.bs.modal', function() {
            resetTaskForm();
        });

        addTaskModal.addEventListener('shown.bs.modal', function() {
            document.getElementById('taskTitle').focus();
        });
    }
}

// События для отдельных заданий
function attachTaskEventListeners() {
    // Чекбоксы для отметки выполнения
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', async function() {
            const taskId = this.dataset.taskId;
            const isCompleted = this.checked;
            const newStatus = isCompleted ? 'completed' : 'assigned';

            try {
                await API.request(`/tasks/${taskId}/status`, 'PATCH', {
                    status: newStatus
                });

                showNotification(
                    `Задание ${isCompleted ? 'отмечено как выполненное' : 'возвращено в работу'}`,
                    'success'
                );

                await loadTasks(); // Обновляем список
            } catch (error) {
                showNotification('Ошибка при обновлении задания', 'danger');
                this.checked = !isCompleted; // Возвращаем чекбокс
            }
        });
    });

    // Кнопки удаления
    document.querySelectorAll('.delete-task-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            taskToDelete = this.dataset.taskId;
            const modal = new bootstrap.Modal(document.getElementById('deleteTaskModal'));
            modal.show();
        });
    });

    // Кнопки редактирования (пока просто открываем модалку с данными)
    document.querySelectorAll('.edit-task-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = this.dataset.taskId;
            const task = currentTasks.find(t => t.id == taskId);

            if (task) {
                // Заполняем форму данными задания
                document.getElementById('taskTitle').value = task.title;
                document.getElementById('taskDescription').value = task.description || '';
                document.getElementById('taskPriority').value = task.priority;
                document.getElementById('taskSubject').value = task.subject_id;

                if (task.deadline) {
                    const deadlineDate = new Date(task.deadline);
                    document.getElementById('hasDeadline').checked = true;
                    document.getElementById('deadlineFields').style.display = 'block';
                    document.getElementById('deadlineDate').valueAsDate = deadlineDate;
                    document.getElementById('deadlineTime').value =
                        deadlineDate.toTimeString().substring(0, 5);
                }

                // Открываем модальное окно
                const modal = new bootstrap.Modal(document.getElementById('addTaskModal'));


                // Меняем заголовок
                document.getElementById('addTaskModalLabel').innerHTML =
                    '<i class="fas fa-edit me-2"></i>Редактировать задание';

                // Помечаем, что это редактирование
                const form = document.getElementById('addTaskForm');
                form.dataset.editMode = 'true';
                form.dataset.editTaskId = taskId;

                // Открываем модальное окно
                modal.show();

            }
        });
    });
}

// Валидация формы задания
function validateTaskForm() {
    const title = document.getElementById('taskTitle').value.trim();
    const subjectId = document.getElementById('taskSubject').value;

    if (!title) {
        showNotification('Введите название задания', 'warning');
        document.getElementById('taskTitle').focus();
        return false;
    }

    if (!subjectId) {
        showNotification('Выберите предмет', 'warning');
        document.getElementById('taskSubject').focus();
        return false;
    }

    return true;
}

// Получение данных формы задания
function getTaskFormData() {
    const hasDeadline = document.getElementById('hasDeadline').checked;
    let deadline = null;

    if (hasDeadline) {
        const date = document.getElementById('deadlineDate').value;
        const time = document.getElementById('deadlineTime').value;

        if (date && time) {
            deadline = new Date(`${date}T${time}`).toISOString();
        }
    }

    return {
        title: document.getElementById('taskTitle').value.trim(),
        description: document.getElementById('taskDescription').value.trim() || null,
        subject_id: parseInt(document.getElementById('taskSubject').value),
        priority: document.getElementById('taskPriority').value,
        deadline: deadline
    };
}

// Вспомогательные функции
function filterTasks(tasks) {
    const now = new Date();

    switch(currentFilter) {
        case 'assigned':
            return tasks.filter(t => t.status === 'assigned');
        case 'completed':
            return tasks.filter(t => t.status === 'completed');
        case 'overdue':
            return tasks.filter(t => {
                if (!t.deadline || t.status === 'completed') return false;
                return new Date(t.deadline) < now;
            });
        default:
            return tasks;
    }
}

function getPriorityClass(priority) {
    switch(priority) {
        case 'high': return 'high-priority';
        case 'low': return 'low-priority';
        default: return '';
    }
}

function getPriorityBadgeClass(priority) {
    switch(priority) {
        case 'high': return 'bg-danger text-white';
        case 'medium': return 'bg-warning text-dark';
        case 'low': return 'bg-secondary text-white';
        default: return 'bg-light text-dark';
    }
}

function getPriorityText(priority) {
    const texts = {
        'high': 'Высокий',
        'medium': 'Средний',
        'low': 'Низкий'
    };
    return texts[priority] || priority;
}

function formatDate(date) {
    return date.toLocaleDateString('ru-RU');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Пагинация
function setupPagination(totalTasks) {
    const container = document.getElementById('paginationContainer');
    container.classList.toggle('d-none', totalTasks <= tasksPerPage);
    updatePaginationInfo();
}

function updatePaginationInfo() {
    const filteredTasks = filterTasks(currentTasks);
    const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);

    document.getElementById('prevPage').disabled = currentPage <= 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
    document.getElementById('pageInfo').textContent = `Страница ${currentPage} из ${totalPages}`;

    const startIndex = (currentPage - 1) * tasksPerPage + 1;
    const endIndex = Math.min(startIndex + tasksPerPage - 1, filteredTasks.length);
    document.getElementById('showingCount').textContent = `${startIndex}-${endIndex}`;
    document.getElementById('totalCount').textContent = filteredTasks.length;
}

// Индикатор загрузки
function showLoading() {
    const container = document.getElementById('tasksContainer');
    container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-2 text-muted">Загружаем задания...</p>
            </div>
        `;
}

function hideLoading() {
    // Ничего не делаем, так как контент уже заменится
}