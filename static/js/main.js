// Основной JavaScript файл для EduVerse

// Инициализация Socket.IO
let socket = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeSocketIO();
});

// Основная инициализация приложения
function initializeApp() {
    console.log('EduVerse приложение инициализировано');
    
    // Анимация появления элементов
    animateElements();
    
    // Инициализация tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Обработчик для модальных окон
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-bs-toggle="modal"]')) {
            const targetModal = e.target.getAttribute('data-bs-target');
            if (targetModal) {
                const modal = new bootstrap.Modal(document.querySelector(targetModal));
                modal.show();
            }
        }
    });
    
    // Обработчик для dropdown меню
    document.addEventListener('click', function(e) {
        if (e.target.matches('.dropdown-toggle')) {
            e.preventDefault();
            const dropdown = e.target.closest('.dropdown');
            dropdown.classList.toggle('show');
        }
    });
    
    // Закрытие dropdown при клике вне его
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropdown-toggle')) {
            const dropdowns = document.querySelectorAll('.dropdown.show');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
}

// Инициализация Socket.IO для чата
function initializeSocketIO() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Подключен к серверу чата');
            updateConnectionStatus(true);
        });
        
        socket.on('disconnect', function() {
            console.log('Отключен от сервера чата');
            updateConnectionStatus(false);
        });
        
        socket.on('message', function(data) {
            displayMessage(data);
        });
        
        socket.on('status', function(data) {
            showNotification(data.msg, 'info');
        });
    }
}

// Анимация появления элементов
function animateElements() {
    const elements = document.querySelectorAll('.feature-card, .role-card, .dashboard-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    });
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

// Функции для чата
function joinChat(chatId) {
    if (socket) {
        socket.emit('join', { room: chatId });
        console.log('Присоединился к чату:', chatId);
    }
}

function leaveChat(chatId) {
    if (socket) {
        socket.emit('leave', { room: chatId });
        console.log('Покинул чат:', chatId);
    }
}

function sendMessage(chatId, message) {
    if (socket && message.trim()) {
        const messageData = {
            room: chatId,
            content: message.trim(),
            timestamp: new Date().toISOString()
        };
        
        socket.emit('message', messageData);
        displayMessage(messageData);
        
        // Очистка поля ввода
        const input = document.querySelector(`#chat-input-${chatId}`);
        if (input) {
            input.value = '';
        }
    }
}

function displayMessage(data) {
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.sender_id === getCurrentUserId() ? 'sent' : 'received'}`;
    
    const time = new Date(data.timestamp).toLocaleTimeString();
    messageDiv.innerHTML = `
        <div class="message-content">${data.content}</div>
        <small class="message-time">${time}</small>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Функции для уведомлений
function showNotification(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.innerHTML = `
        <div class="toast-body">
            ${message}
            <button type="button" class="btn-close btn-close-white ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Функции для календаря
function initializeCalendar(containerId, events = []) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    renderCalendar(container, currentMonth, currentYear, events);
}

function renderCalendar(container, month, year, events) {
    const monthNames = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();
    
    let calendarHTML = `
        <div class="calendar-header">
            <button class="btn btn-sm btn-outline-primary" onclick="changeMonth(${month - 1}, ${year})">
                <i class="fas fa-chevron-left"></i>
            </button>
            <h5 class="mb-0">${monthNames[month]} ${year}</h5>
            <button class="btn btn-sm btn-outline-primary" onclick="changeMonth(${month + 1}, ${year})">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>
        <div class="calendar-grid">
    `;
    
    // Дни недели
    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    weekDays.forEach(day => {
        calendarHTML += `<div class="calendar-day-header">${day}</div>`;
    });
    
    // Пустые ячейки в начале месяца
    for (let i = 0; i < startingDay; i++) {
        calendarHTML += '<div class="calendar-day empty"></div>';
    }
    
    // Дни месяца
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const isToday = date.toDateString() === new Date().toDateString();
        const hasEvent = events.some(event => {
            const eventDate = new Date(event.date);
            return eventDate.toDateString() === date.toDateString();
        });
        
        let dayClass = 'calendar-day';
        if (isToday) dayClass += ' today';
        if (hasEvent) dayClass += ' has-event';
        
        calendarHTML += `<div class="${dayClass}" onclick="selectDate(${day}, ${month}, ${year})">${day}</div>`;
    }
    
    calendarHTML += '</div>';
    container.innerHTML = calendarHTML;
}

function changeMonth(month, year) {
    if (month < 0) {
        month = 11;
        year--;
    } else if (month > 11) {
        month = 0;
        year++;
    }
    
    const container = document.querySelector('.calendar-widget');
    if (container) {
        renderCalendar(container, month, year, []);
    }
}

function selectDate(day, month, year) {
    const selectedDate = new Date(year, month, day);
    console.log('Выбрана дата:', selectedDate.toLocaleDateString());
    
    // Здесь можно добавить логику для показа событий на выбранную дату
    showNotification(`Выбрана дата: ${selectedDate.toLocaleDateString()}`, 'info');
}

// Функции для оценок
function displayGrades(grades) {
    const container = document.querySelector('.grades-container');
    if (!container) return;
    
    let gradesHTML = `
        <table class="table table-striped grade-table">
            <thead>
                <tr>
                    <th>Предмет</th>
                    <th>Оценка</th>
                    <th>Дата</th>
                    <th>Комментарий</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    grades.forEach(grade => {
        const gradeClass = getGradeClass(grade.grade);
        gradesHTML += `
            <tr>
                <td>${grade.subject_name}</td>
                <td><span class="grade-badge ${gradeClass}">${grade.grade}</span></td>
                <td>${new Date(grade.date).toLocaleDateString()}</td>
                <td>${grade.comment || '-'}</td>
            </tr>
        `;
    });
    
    gradesHTML += '</tbody></table>';
    container.innerHTML = gradesHTML;
}

function getGradeClass(grade) {
    if (grade >= 9) return 'grade-excellent';
    if (grade >= 7) return 'grade-good';
    if (grade >= 5) return 'grade-average';
    return 'grade-poor';
}

// Функции для платежей
function displayPayments(payments) {
    const container = document.querySelector('.payments-container');
    if (!container) return;
    
    let paymentsHTML = `
        <div class="row g-3">
    `;
    
    payments.forEach(payment => {
        const statusClass = getPaymentStatusClass(payment.status);
        const progressPercent = (payment.paid_amount / payment.amount) * 100;
        
        paymentsHTML += `
            <div class="col-md-6 col-lg-4">
                <div class="card payment-card">
                    <div class="card-body">
                        <h6 class="card-title">${payment.month}/${payment.year}</h6>
                        <div class="payment-status ${statusClass} mb-2">
                            ${getPaymentStatusText(payment.status)}
                        </div>
                        <div class="payment-amount">
                            <strong>Сумма:</strong> ${payment.amount} ₽
                        </div>
                        <div class="payment-paid">
                            <strong>Оплачено:</strong> ${payment.paid_amount} ₽
                        </div>
                        <div class="progress mt-2">
                            <div class="progress-bar" style="width: ${progressPercent}%"></div>
                        </div>
                        <div class="payment-due-date mt-2">
                            <small class="text-muted">Срок: ${new Date(payment.due_date).toLocaleDateString()}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    paymentsHTML += '</div>';
    container.innerHTML = paymentsHTML;
}

function getPaymentStatusClass(status) {
    switch (status) {
        case 'paid': return 'payment-paid';
        case 'partial': return 'payment-partial';
        case 'due': return 'payment-due';
        default: return 'payment-due';
    }
}

function getPaymentStatusText(status) {
    switch (status) {
        case 'paid': return 'Оплачено';
        case 'partial': return 'Частично';
        case 'due': return 'К оплате';
        default: return 'Неизвестно';
    }
}

// Функции для расписания
function displaySchedule(schedule) {
    const container = document.querySelector('.schedule-container');
    if (!container) return;
    
    const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'];
    
    let scheduleHTML = `
        <div class="schedule-tabs">
            <ul class="nav nav-tabs" id="scheduleTabs" role="tablist">
    `;
    
    daysOfWeek.forEach((day, index) => {
        const isActive = index === 0 ? 'active' : '';
        scheduleHTML += `
            <li class="nav-item" role="presentation">
                <button class="nav-link ${isActive}" id="day-${index}-tab" data-bs-toggle="tab" 
                        data-bs-target="#day-${index}" type="button" role="tab">
                    ${day}
                </button>
            </li>
        `;
    });
    
    scheduleHTML += '</ul><div class="tab-content mt-3">';
    
    daysOfWeek.forEach((day, index) => {
        const isActive = index === 0 ? 'active' : '';
        const daySchedule = schedule.filter(item => item.day_of_week === index);
        
        scheduleHTML += `
            <div class="tab-pane fade ${isActive}" id="day-${index}" role="tabpanel">
                <div class="schedule-day">
        `;
        
        if (daySchedule.length === 0) {
            scheduleHTML += '<p class="text-muted">Нет занятий</p>';
        } else {
            daySchedule.sort((a, b) => new Date('2000-01-01 ' + a.start_time) - new Date('2000-01-01 ' + b.start_time));
            
            daySchedule.forEach(item => {
                scheduleHTML += `
                    <div class="schedule-item">
                        <div class="schedule-time">
                            ${item.start_time} - ${item.end_time}
                        </div>
                        <div class="schedule-subject">
                            <strong>${item.subject_name}</strong>
                        </div>
                        <div class="schedule-teacher">
                            ${item.teacher_name}
                        </div>
                        <div class="schedule-room">
                            Кабинет: ${item.room || 'Не указан'}
                        </div>
                    </div>
                `;
            });
        }
        
        scheduleHTML += '</div></div>';
    });
    
    scheduleHTML += '</div></div>';
    container.innerHTML = scheduleHTML;
}

// Утилитарные функции
function getCurrentUserId() {
    // Получение ID текущего пользователя из данных страницы
    const userElement = document.querySelector('[data-user-id]');
    return userElement ? userElement.dataset.userId : null;
}

function updateConnectionStatus(connected) {
    const statusElement = document.querySelector('.connection-status');
    if (statusElement) {
        statusElement.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        statusElement.textContent = connected ? 'Подключен' : 'Отключен';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

function formatTime(timeString) {
    return timeString.substring(0, 5);
}

// Экспорт функций для использования в других модулях
window.EduVerse = {
    joinChat,
    leaveChat,
    sendMessage,
    showNotification,
    initializeCalendar,
    displayGrades,
    displayPayments,
    displaySchedule,
    formatDate,
    formatTime
};