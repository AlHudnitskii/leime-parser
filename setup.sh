#!/bin/bash
# Скрипт настройки VPS сервера (Ubuntu 22.04)
# Запускать от root: bash setup_server.sh

set -e

echo "=== Установка Docker ==="
apt-get update -q
apt-get install -y docker.io docker-compose-plugin git

echo "=== Создание рабочей директории ==="
mkdir -p /opt/casino-scraper/output
cd /opt/casino-scraper

echo "=== Копируем файлы проекта ==="
# Предполагается что файлы уже загружены в /opt/casino-scraper/
# scp -r ./casino-scraper/* root@ВАШ_IP:/opt/casino-scraper/

echo "=== Генерация токена ==="
TOKEN=$(openssl rand -hex 16)
echo "Ваш токен: $TOKEN"
echo "Вставьте его в docker-compose.yml и scraper.py"

echo "=== Запуск Chrome контейнера ==="
docker compose up -d chrome

echo "=== Проверка что Chrome поднялся ==="
sleep 5
curl -s http://localhost:3000/json/version | python3 -m json.tool

echo ""
echo "=== Установка Python зависимостей ==="
apt-get install -y python3-pip
pip3 install playwright beautifulsoup4 lxml
playwright install chromium

echo ""
echo "=== Настройка cron (каждый день в 3:00) ==="
CRON_JOB="0 3 * * * cd /opt/casino-scraper && python3 scraper.py >> /var/log/casino-scraper.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "========================================"
echo "Готово! Запустите первый раз вручную:"
echo "  cd /opt/casino-scraper && python3 scraper.py"
echo ""
echo "Логи: tail -f /var/log/casino-scraper.log"
echo "Результаты: /opt/casino-scraper/output/"
echo "========================================"