#!/bin/bash

# Обработчик Ctrl+C
cleanup()
{
    echo ""
    echo "[INFO] Завершаю все процессы..."

    # Аккуратно убиваем server.py
    if [[ -n "$SERVER_PID" ]]; then
        echo "[INFO] Завершаю server.py (PID $SERVER_PID)..."
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null
    fi

    # Аккуратно убиваем rosbridge_websocket
    if [[ -n "$LAUNCH2_PID" ]]; then
        echo "[INFO] Завершаю rosbridge_websocket.launch (PID $LAUNCH2_PID)..."
        kill $LAUNCH2_PID
        wait $LAUNCH2_PID 2>/dev/null
    fi

    # Аккуратно убиваем moveit_planning_execution
    if [[ -n "$LAUNCH1_PID" ]]; then
        echo "[INFO] Завершаю custom_moveit_planning_execution.launch (PID $LAUNCH1_PID)..."
        kill $LAUNCH1_PID
        wait $LAUNCH1_PID 2>/dev/null
    fi

    # И наконец roscore
    if [[ -n "$ROSCORE_PID" ]]; then
        echo "[INFO] Завершаю roscore (PID $ROSCORE_PID)..."
        kill $ROSCORE_PID
        wait $ROSCORE_PID 2>/dev/null
    fi

    echo "[INFO] Все процессы завершены. Выход."
    exit 0
}

# Навешиваем ловушку на SIGINT
trap cleanup SIGINT

# Запуск процессов
echo "[INFO] Запускаю roscore..."
roscore &
ROSCORE_PID=$!

echo "[INFO] Жду запуска roscore..."
until rostopic list > /dev/null 2>&1
do
    sleep 1
done

echo "[INFO] roscore запущен успешно!"

echo "[INFO] Запуск custom_moveit_planning_execution.launch..."
roslaunch kuka_kr10_updated_config custom_moveit_planning_execution.launch &
LAUNCH1_PID=$!

sleep 2

echo "[INFO] Запуск rosbridge_websocket.launch..."
roslaunch rosbridge_server rosbridge_websocket.launch &
LAUNCH2_PID=$!

sleep 2

echo "[INFO] Запуск server.py..."
python3 src/kuka_kr10_updated_config/test/server.py &
SERVER_PID=$!

# Ожидание всех процессов
wait $ROSCORE_PID $LAUNCH1_PID $LAUNCH2_PID $SERVER_PID
