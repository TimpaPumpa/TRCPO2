import multiprocessing
import time


# Функція для визначення кількості кроків відповідно до гіпотези Коллатца

def collatz_steps(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps


# Функція-працівник для виконання в процесі

def worker(task_queue, result_queue):
    total_steps = 0
    max_steps = 0
    max_number = 0
    count = 0
    while True:
        number = task_queue.get()
        if number is None:
            break
        steps = collatz_steps(number)
        total_steps += steps
        count += 1
        if steps > max_steps:
            max_steps = steps
            max_number = number
    result_queue.put((total_steps, count, max_steps, max_number))


# Функція для запуску обчислень із заданою кількістю процесів

def collatz_parallel(NUMBERS_COUNT, PROCESSES_COUNT):
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # Додаємо всі числа до черги завдань
    for number in range(1, NUMBERS_COUNT + 1):
        task_queue.put(number)

    processes = []  # Створюємо процеси
    for _ in range(PROCESSES_COUNT):
        process = multiprocessing.Process(target=worker, args=(task_queue, result_queue))
        process.start()
        processes.append(process)

    # Додаємо маркери завершення (None) для кожного процесу
    for _ in range(PROCESSES_COUNT):
        task_queue.put(None)

    # Чекаємо завершення всіх процесів
    for process in processes:
        process.join()

    # Обчислюємо загальні результати
    total_steps = 0
    total_count = 0
    global_max_steps = 0
    global_max_number = 1

    while not result_queue.empty():
        steps, count, max_steps, max_number = result_queue.get()
        total_steps += steps
        total_count += count
        if max_steps > global_max_steps:
            global_max_steps = max_steps
            global_max_number = max_number

    # Обчислюємо середню кількість кроків
    average_steps = total_steps / total_count
    return average_steps, global_max_steps, global_max_number


# Функція для тестування з різною кількістю процесів

def test_with_processes(NUMBERS_COUNT, process_counts):
    for process_count in process_counts:
        print(f"\nЗапуск з {process_count} процесами...")
        start_time = time.time()
        average_steps, max_steps, max_number = collatz_parallel(NUMBERS_COUNT, process_count)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Середня кількість кроків: {average_steps:.2f}")
        print(f"Найбільше число: {max_number} з {max_steps} кроками")
        print(f"Час виконання: {elapsed_time:.2f} секунд")


if __name__ == "__main__":
    NUMBERS_COUNT = 100000  # Кількість чисел для обчислення
    process_counts = [1, 2, 10, 12, 50]  # Кількість процесів для тестування
    test_with_processes(NUMBERS_COUNT, process_counts)
