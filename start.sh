#!/bin/bash

# EduVerse - Скрипт запуска
# Автор: EduVerse Team
# Версия: 1.0.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не найден. Установите Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Требуется Python 3.8+, текущая версия: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION найден"
}

# Проверка наличия pip
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 не найден. Установите pip"
        exit 1
    fi
    
    print_success "pip3 найден"
}

# Создание виртуального окружения
create_venv() {
    if [ ! -d "venv" ]; then
        print_status "Создание виртуального окружения..."
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    else
        print_status "Виртуальное окружение уже существует"
    fi
}

# Активация виртуального окружения
activate_venv() {
    print_status "Активация виртуального окружения..."
    source venv/bin/activate
    print_success "Виртуальное окружение активировано"
}

# Установка зависимостей
install_dependencies() {
    print_status "Установка зависимостей..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Зависимости установлены"
}

# Создание необходимых директорий
create_directories() {
    print_status "Создание необходимых директорий..."
    mkdir -p uploads logs backups instance
    print_success "Директории созданы"
}

# Проверка конфигурации
check_config() {
    if [ ! -f ".env" ]; then
        print_warning "Файл .env не найден. Создание из примера..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Файл .env создан из примера. Отредактируйте его перед запуском!"
            print_warning "Особое внимание уделите SECRET_KEY!"
        else
            print_error "Файл .env.example не найден"
            exit 1
        fi
    fi
}

# Проверка базы данных
check_database() {
    if [ ! -f "instance/eduverse.db" ]; then
        print_status "База данных не найдена. Она будет создана автоматически при первом запуске."
    else
        print_success "База данных найдена"
    fi
}

# Запуск приложения
start_app() {
    print_status "Запуск EduVerse..."
    print_success "Приложение будет доступно по адресу: http://localhost:5000"
    print_success "Для остановки нажмите Ctrl+C"
    echo ""
    
    # Запуск с автоматическим созданием БД
    python app.py
}

# Основная функция
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    EduVerse Launcher                        ║"
    echo "║              Образовательная платформа                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Проверки
    check_python
    check_pip
    
    # Настройка окружения
    create_venv
    activate_venv
    install_dependencies
    create_directories
    check_config
    check_database
    
    # Запуск
    start_app
}

# Обработка сигналов
trap 'echo ""; print_warning "Получен сигнал остановки. Завершение работы..."; exit 0' INT TERM

# Запуск основной функции
main "$@"