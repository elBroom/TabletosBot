# TabletosBot
Телеграмм бот напоминающий пить таблеточки и журналирующий принятую дозировку.

Ссылка на бот: https://t.me/TabletossBot

### Запуск:
```bash
docker-compose build
cp config.example.py config.py
vim config.py
# edit config.py
python3 init_db.py
docker-compose up -d
```

### TODO:
- [x] Добавление напоминания
- [x] Отправка напоминаний по расписанию
- [x] Удаление напоминания
- [x] Удаление всех напоминаний
- [x] Сохранение состояния после перезагрузки (sqllite)
- [x] Остановка напоминания
- [x] Включение напоминания
- [x] Остановка всех напоминаний
- [x] Введение журнала принятых таблеток
- [x] Удаление записи из дневника
- [x] Автоматическое откладывание напоминания
- [x] Подтверждение принятой таблетки
- [x] Возможность отложить напоминание
- [x] Установка timezone
- [x] Настройка интервала напоминания
- [x] Настройка настойчивости бота
- [x] Подтверждение принятой таблетки с фото
- [x] Пропуск шага отправки фото
- [x] Написать help и настроить бот 
- [x] Отправка журнала в csv формате
- [x] Настроить CI
- [x] Получение timezone из локации
- [x] Логирование ошибок в sentry
- [x] Логирование действий
- [x] Редактирование настроек
- [x] Удаление персональных данных
------
- [ ] Сохранять отложенные напоминания
- [ ] Отрисовка журнала в виде графика
- [ ] Написать тесты
- [ ] Введение журнала побочных эффектов
- [ ] Поддержка английского языка
