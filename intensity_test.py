import socket
import json
import time
import csv
from pathlib import Path

import matplotlib.pyplot as plt


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

MEASUREMENTS_COUNT = 1000
TIMEOUT = 2.0

# Интервал между пакетами, с.
# Чем меньше интервал — тем выше интенсивность.
INTENSITIES = [
    0.1,    # 10 пакетов/с
    0.05,   # 20 пакетов/с
    0.01,   # 100 пакетов/с
    0.005   # 200 пакетов/с
]

RESULTS_DIR = Path("intensity_results")


def measure_rtt(
    client_socket,
    sequence_number
):
    message = {
        "sequence_number": sequence_number
    }

    data = json.dumps(message).encode(
        "utf-8"
    )

    send_time = time.perf_counter_ns()

    client_socket.sendto(
        data,
        (SERVER_HOST, SERVER_PORT)
    )

    response_data, _ = client_socket.recvfrom(
        4096
    )

    receive_time = time.perf_counter_ns()

    json.loads(
        response_data.decode("utf-8")
    )

    rtt_ms = (
        receive_time - send_time
    ) / 1_000_000

    return rtt_ms


def calculate_jitter(rtt_values):
    """
    J_i = |RTT_i - RTT_(i-1)|
    """

    variations = []

    for i in range(1, len(rtt_values)):
        variation = abs(
            rtt_values[i]
            - rtt_values[i - 1]
        )

        variations.append(variation)

    if not variations:
        return [], 0.0

    average_jitter = (
        sum(variations)
        / len(variations)
    )

    return variations, average_jitter


def save_raw_results(
    packets_per_second,
    rtt_values,
    jitter_values
):
    filename = (
        RESULTS_DIR
        / f"raw_{packets_per_second:.0f}pps.csv"
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "sequence_number",
            "rtt_ms",
            "jitter_ms"
        ])

        for i, rtt in enumerate(
            rtt_values,
            start=1
        ):
            if i == 1:
                jitter = ""
            else:
                jitter = jitter_values[i - 2]

            writer.writerow([
                i,
                rtt,
                jitter
            ])


def run_test(interval):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    client_socket.settimeout(TIMEOUT)

    rtt_values = []

    packets_per_second = 1 / interval

    print()
    print(
        f"Интенсивность: "
        f"{packets_per_second:.0f} пакетов/с"
    )

    print(
        f"Интервал: {interval} с"
    )

    for sequence_number in range(
        1,
        MEASUREMENTS_COUNT + 1
    ):
        try:
            rtt = measure_rtt(
                client_socket,
                sequence_number
            )

            rtt_values.append(rtt)

        except socket.timeout:
            print(
                f"Тайм-аут: пакет "
                f"{sequence_number}"
            )

        if interval > 0:
            time.sleep(interval)

    client_socket.close()

    if len(rtt_values) < 2:
        print(
            "Недостаточно успешных измерений."
        )
        return None

    jitter_values, average_jitter = (
        calculate_jitter(rtt_values)
    )

    average_rtt = (
        sum(rtt_values)
        / len(rtt_values)
    )

    maximum_jitter = max(
        jitter_values
    )

    save_raw_results(
        packets_per_second,
        rtt_values,
        jitter_values
    )

    return {
        "interval": interval,
        "packets_per_second":
            packets_per_second,
        "successful_measurements":
            len(rtt_values),
        "average_rtt_ms":
            average_rtt,
        "average_jitter_ms":
            average_jitter,
        "maximum_jitter_ms":
            maximum_jitter,
        "rtt_values":
            rtt_values,
        "jitter_values":
            jitter_values
    }


def save_summary(results):
    output_file = (
        RESULTS_DIR
        / "intensity_results.csv"
    )

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "interval",
                "packets_per_second",
                "successful_measurements",
                "average_rtt_ms",
                "average_jitter_ms",
                "maximum_jitter_ms"
            ]
        )

        writer.writeheader()

        for result in results:
            writer.writerow({
                "interval":
                    result["interval"],

                "packets_per_second":
                    result["packets_per_second"],

                "successful_measurements":
                    result[
                        "successful_measurements"
                    ],

                "average_rtt_ms":
                    result["average_rtt_ms"],

                "average_jitter_ms":
                    result[
                        "average_jitter_ms"
                    ],

                "maximum_jitter_ms":
                    result[
                        "maximum_jitter_ms"
                    ]
            })


def plot_rtt(results):
    plt.figure(figsize=(10, 5))

    for result in results:
        plt.plot(
            result["rtt_values"],
            label=(
                f'{result["packets_per_second"]:.0f} '
                f'пакетов/с'
            )
        )

    plt.xlabel("Номер измерения")
    plt.ylabel("RTT, мс")

    plt.title(
        "Изменение RTT при различных "
        "интенсивностях передачи"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR
        / "rtt_by_intensity.png",
        dpi=150
    )

    plt.close()


def plot_jitter(results):
    plt.figure(figsize=(10, 5))

    for result in results:
        plt.plot(
            result["jitter_values"],
            label=(
                f'{result["packets_per_second"]:.0f} '
                f'пакетов/с'
            )
        )

    plt.xlabel("Номер измерения")
    plt.ylabel("Джиттер, мс")

    plt.title(
        "Изменение джиттера при различных "
        "интенсивностях передачи"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR
        / "jitter_by_intensity.png",
        dpi=150
    )

    plt.close()


def print_summary(results):
    print()
    print("Результаты эксперимента:")
    print("-" * 78)

    print(
        f"{'Пакетов/с':>12} "
        f"{'Измерений':>12} "
        f"{'Средний RTT':>15} "
        f"{'Средний джиттер':>18} "
        f"{'Макс. джиттер':>15}"
    )

    print("-" * 78)

    for result in results:
        print(
            f"{result['packets_per_second']:>12.0f} "
            f"{result['successful_measurements']:>12} "
            f"{result['average_rtt_ms']:>15.3f} "
            f"{result['average_jitter_ms']:>18.3f} "
            f"{result['maximum_jitter_ms']:>15.3f}"
        )

    print("-" * 78)


def main():
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = []

    print(
        "Начало эксперимента "
        "с различными интенсивностями."
    )

    for interval in INTENSITIES:
        result = run_test(interval)

        if result is not None:
            results.append(result)

    if not results:
        print(
            "Не удалось получить результаты."
        )
        return

    save_summary(results)

    plot_rtt(results)
    plot_jitter(results)

    print_summary(results)

    print()
    print(
        f"Результаты сохранены в: "
        f"{RESULTS_DIR}"
    )

    print()
    print("Созданы файлы:")
    print("  - intensity_results.csv")
    print("  - rtt_by_intensity.png")
    print("  - jitter_by_intensity.png")
    print("  - raw_*pps.csv")


if __name__ == "__main__":
    main()