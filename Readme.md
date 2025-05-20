# KUKA KR10 R1420 - ROS MoveIt Integration Project

Этот проект представляет собой настройку рабочего пространства ROS (`kuka_ws`) для работы с промышленным роботом **KUKA KR10 R1420** с использованием **MoveIt**.

---

## 📁 Структура проекта

```
kuka_ws/
  src/
    kuka_kr10_support/        # Файлы xacro/urdf робота
    kuka_kr10_moveit_config/   # Конфигурация MoveIt (группы, планировщик, kinematics.yaml)
      config/
      launch/
    test/
      move_to_xyz.py           # Скрипт передачи X Y Z + кватерниона
```

---

## 🌍 Что сделано

### Инфраструктура
- Создано catkin-рабочее пространство (`kuka_ws`).
- Подготовлены файлы URDF/XACRO робота KR10 R1420.
- Добавлен простой вакуумный гриппер (`vacuum_gripper`) как новый `link`.

### MoveIt
- Сгенерирован конфиг `kuka_kr10_moveit_config` через MoveIt Setup Assistant.
- Планировочная группа `manipulator` (шесть суставов).
- Установлен OPW Kinematics Plugin (быстрая аналитическая инверсная кинематика).
- Выставлены параметры:
  - `kinematics_solver_timeout: 0.5`
  - `planning_time: 5.0 sec`
  - `num_planning_attempts: 10`
  - `goal_orientation_tolerance: 3.14`

### Тесты
- Создан скрипт `move_to_xyz.py`:
  - Принимает X, Y, Z, qx, qy, qz, qw.
  - Устанавливает цель для манипулятора.
  - Строит план и эмулирует движение.
- Чтение текущих значений суставов через `get_current_joint_values()`.

---

## 🚀 Как использовать

1. Запустить MoveIt:
    ```bash
    roslaunch kuka_kr10_moveit_config demo.launch
    ```
2. В новом терминале запустить скрипт для отправки позиции:
    ```bash
    python3 ~/kuka_ws/src/kuka_kr10_moveit_config/test/move_to_xyz.py 0.5 0.0 0.3 1 0 0 0
    ```

---
## Демонстрация в Unity

![{69EFC3BB-BE12-4690-8069-3A880E789C99}](https://github.com/user-attachments/assets/90c9f6fa-50f1-49e3-a7fd-bebea475851d)
