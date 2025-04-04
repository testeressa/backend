import subprocess
from collections import defaultdict
import datetime
import os


def parse_processes():
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    processes = lines[1:]

    users = defaultdict(int)
    total_processes = len(processes)
    total_memory = 0.0
    total_cpu = 0.0
    max_memory_process = ('', 0.0)
    max_cpu_process = ('', 0.0)

    for line in processes:
        parts = line.split()
        user = parts[0]
        cpu = float(parts[2])
        memory = float(parts[3])
        command = ' '.join(parts[10:])

        users[user] += 1
        total_memory += memory
        total_cpu += cpu

        if memory > max_memory_process[1]:
            max_memory_process = (command[:20], memory)

        if cpu > max_cpu_process[1]:
            max_cpu_process = (command[:20], cpu)

        report = [
            "Отчёт о состоянии системы:",
            f"Пользователи системы: {', '.join(sorted(users.keys()))}",
            f"Процессов запущено: {total_processes}",
            "",
            "Пользовательских процессов:"
        ]

        for user, count in sorted(users.items()):
            report.append(f"{user}: {count}")

        report.extend([
            "",
            f"Всего памяти используется: {total_memory:.1f}%",
            f"Всего CPU используется: {total_cpu:.1f}%",
            f"Больше всего памяти использует: {max_memory_process[0]} ({max_memory_process[1]:.1f}%)",
            f"Больше всего CPU использует: {max_cpu_process[0]} ({max_cpu_process[1]:.1f}%)"
        ])

    print('\n'.join(report))

    timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M")
    filename = f"{timestamp}-scan.txt"

    with open(filename, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nОтчёт сохранён в файл: {os.path.abspath(filename)}")


parse_processes()

