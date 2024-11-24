import concurrent.futures
import threading
import time
import ctypes


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


# Функція-працівник для виконання завдання

def worker(number, total_steps, max_steps, max_number, lock):
    steps = collatz_steps(number)
    with lock:
        ctypes.windll.kernel32.InterlockedAdd(ctypes.byref(total_steps), steps)
        ctypes.windll.kernel32.InterlockedIncrement(ctypes.byref(max_number))
        if steps > max_steps.value:
            max_steps.value = steps
            max_number.value = number


# Функція для запуску обчислень із використанням ThreadPool

def collatz_parallel(NUMBERS_COUNT, MAX_WORKERS):
    total_steps = ctypes.c_int(0)
    max_steps = ctypes.c_int(0)
    max_number = ctypes.c_int(1)
    lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(worker, number, total_steps, max_steps, max_number, lock) for number in
                   range(1, NUMBERS_COUNT + 1)]
        concurrent.futures.wait(futures)

    # Обчислюємо середню кількість кроків
    average_steps = total_steps.value / NUMBERS_COUNT
    return average_steps, max_steps.value, max_number.value


# Функція для тестування з різною кількістю потоків

def test_with_threads(NUMBERS_COUNT, thread_counts):
    for thread_count in thread_counts:
        print(f"\nЗапуск з {thread_count} потоками...")
        start_time = time.time()
        average_steps, max_steps, max_number = collatz_parallel(NUMBERS_COUNT, thread_count)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Середня кількість кроків: {average_steps:.2f}")
        print(f"Найбільше число: {max_number} з {max_steps} кроками")
        print(f"Час виконання: {elapsed_time:.2f} секунд")


if __name__ == "__main__":
    NUMBERS_COUNT = 100000  # Кількість чисел для обчислення
    thread_counts = [1, 2, 10, 12, 50]  # Кількість потоків для тестування
    test_with_threads(NUMBERS_COUNT, thread_counts)
