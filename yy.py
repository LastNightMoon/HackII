import subprocess

# Путь к твоему скрипту .sh
script_path = "./hh.sh"

# Запускаем скрипт и ждём окончания
result = subprocess.run(["bash", script_path], capture_output=True, text=True)

# Выводим stdout и stderr для отладки
print("stdout:", result.stdout)
print("stderr:", result.stderr)

# Проверяем код возврата (0 — успех)
if result.returncode == 0:
    print("Скрипт выполнен успешно!")
else:
    print(f"Ошибка выполнения скрипта, код {result.returncode}")
