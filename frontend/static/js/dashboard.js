function getSubjectStats() {
    return API.request('/users/stats')
}

document.addEventListener('DOMContentLoaded', function() {
    // Загрузка статистики
    async function loadDashboardStats() {
        try {
            // Загрузка общих статистик
            const statsResponse = await API.request('/tasks/stats/summary');
            if (statsResponse) {
                document.getElementById('total-tasks-dash').textContent = statsResponse.total || 0;
                document.getElementById('completed-tasks-dash').textContent = statsResponse.completed || 0;
                document.getElementById('active-tasks-dash').textContent = statsResponse.assigned || 0;
                document.getElementById('overdue-tasks-dash').textContent = statsResponse.overdue || 0;

                // Расчет прогресса
                const total = statsResponse.total || 1;
                const completed = statsResponse.completed || 0;
                const progressPercent = Math.round((completed / total) * 100);

                const progressBar = document.getElementById('progress-bar');
                const progressText = document.getElementById('progress-text');

                progressBar.style.width = progressPercent + '%';
                progressBar.setAttribute('aria-valuenow', progressPercent);
                progressText.textContent = progressPercent + '%';
            }

            // Загрузка ближайших заданий
            const tasksResponse = await API.request('/tasks?limit=5&sort=deadline&status=assigned');
            if (tasksResponse && tasksResponse.tasks) {
                const tasksContainer = document.getElementById('upcoming-tasks');
                if (tasksResponse.tasks.length > 0) {
                    tasksContainer.innerHTML = tasksResponse.tasks.map(task => `
                            <div class="task-item mb-3 p-3 border rounded">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="mb-1">${task.title}</h6>
                                        <small class="text-muted">
                                            <i class="fas fa-book me-1"></i>${task.subject_name || 'Без предмета'}
                                            <span class="mx-2">•</span>
                                            <i class="fas fa-clock me-1"></i>${task.deadline ? new Date(task.deadline).toLocaleDateString() : 'Нет срока'}
                                        </small>
                                    </div>
                                    <span class="badge bg-${task.priority === 'high' ? 'danger' : task.priority === 'medium' ? 'warning' : 'info'}">
                                        ${task.priority === 'high' ? 'Высокий' : task.priority === 'medium' ? 'Средний' : 'Низкий'} приоритет
                                    </span>
                                </div>
                            </div>
                        `).join('');
                } else {
                    tasksContainer.innerHTML = `
                            <div class="text-center py-4">
                                <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                                <h5>Все задачи выполнены!</h5>
                                <p class="text-muted">Нет ближайших дедлайнов.</p>
                            </div>
                        `;
                }
            }

            // Загрузка предметов
            // API.request('/subjects');
            const subjectsResponse = await API.request('/subjects')
            if (subjectsResponse) {
                let html = '';
                const stats = await getSubjectStats()
                // console.log(subjectsResponse);
                const subjectsContainer = document.getElementById('subjects-list');
                if (subjectsResponse.length > 0) {
                    subjectsResponse.forEach(subject => {
                        const subjectStats = stats.subject_stats.find(s => s.subject_id === subject.id);

                        html += `
                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                                <div class="d-flex align-items-center">
                                    <div class="color-dot me-2" style="background-color: ${subject.color}; width: 12px; height: 12px; border-radius: 50%;"></div>
                                    <span>${subject.name}</span>
                                </div>
                                <span class="badge bg-secondary">${subjectStats.inProcess_tasks || 0}</span>
                            </div>
                        `
                    })

                    subjectsContainer.innerHTML = html;
                    //     subjectsContainer.innerHTML = subjectsResponse.map(subject => `
                    //         <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                    //             <div class="d-flex align-items-center">
                    //                 <div class="color-dot me-2" style="background-color: ${subject.color}; width: 12px; height: 12px; border-radius: 50%;"></div>
                    //                 <span>${subject.name}</span>
                    //             </div>
                    //             <span class="badge bg-secondary">${subject.task_count || 0}</span>
                    //         </div>
                    //     `).join('');
                } else {
                    subjectsContainer.innerHTML = `
                            <div class="text-center py-3">
                                <p class="text-muted mb-2">Нет добавленных предметов</p>
                            </div>
                        `;
                }
            }

        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    loadDashboardStats();

    // Обновление данных каждые 5 минут
    setInterval(loadDashboardStats, 5 * 60 * 1000);
});