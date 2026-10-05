import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


INPUT_FILE = "rtt_results.csv"
RESULTS_DIR = Path("analysis_results")


def load_data(filename):
    sequence_numbers = []
    rtt_values = []

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            sequence_numbers.append(
                int(row["sequence_number"])
            )

            rtt_values.append(
                float(row["rtt_ms"])
            )

    return sequence_numbers, rtt_values


def percentile(values, percent):
    sorted_values = sorted(values)

    position = (
        (len(sorted_values) - 1)
        * percent
        / 100
    )

    lower = int(position)
    upper = lower + 1

    if upper >= len(sorted_values):
        return sorted_values[lower]

    fraction = position - lower

    return (
        sorted_values[lower]
        + (
            sorted_values[upper]
            - sorted_values[lower]
        )
        * fraction
    )


def calculate_statistics(values):
    return {
        "Среднее": statistics.mean(values),
        "Медиана": statistics.median(values),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "Минимум": min(values),
        "Максимум": max(values)
    }


def calculate_jitter(rtt_values):
    """
    Джиттер рассчитывается как абсолютная
    разность соседних значений RTT:

        J_i = |RTT_i - RTT_(i-1)|

    Итоговый показатель:

        J = mean(J_i)
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

    average_jitter = statistics.mean(
        variations
    )

    return variations, average_jitter


def save_statistics(
    statistics_data,
    jitter
):
    filename = (
        RESULTS_DIR / "statistics.txt"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "Статистические характеристики RTT\n"
        )
        file.write("=" * 40 + "\n\n")

        for name, value in statistics_data.items():
            file.write(
                f"{name}: {value:.6f} мс\n"
            )

        file.write("\n")
        file.write(
            f"Средний джиттер: "
            f"{jitter:.6f} мс\n"
        )


def plot_rtt(
    sequence_numbers,
    rtt_values
):
    plt.figure(figsize=(10, 5))

    plt.plot(
        sequence_numbers,
        rtt_values
    )

    plt.xlabel("Номер измерения")
    plt.ylabel("RTT, мс")
    plt.title("Изменение RTT во времени")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "rtt_over_time.png",
        dpi=150
    )

    plt.close()


def plot_histogram(rtt_values):
    plt.figure(figsize=(10, 5))

    plt.hist(
        rtt_values,
        bins=30
    )

    plt.xlabel("RTT, мс")
    plt.ylabel("Количество измерений")
    plt.title("Распределение RTT")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "rtt_histogram.png",
        dpi=150
    )

    plt.close()


def plot_jitter(
    sequence_numbers,
    rtt_values,
    variations
):
    jitter_numbers = sequence_numbers[1:]

    plt.figure(figsize=(10, 5))

    plt.plot(
        jitter_numbers,
        rtt_values[1:],
        label="RTT"
    )

    plt.plot(
        jitter_numbers,
        variations,
        label="Джиттер"
    )

    plt.xlabel("Номер измерения")
    plt.ylabel("Значение, мс")
    plt.title(
        "Изменение задержки и джиттера"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "delay_and_jitter.png",
        dpi=150
    )

    plt.close()


def main():
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    sequence_numbers, rtt_values = load_data(
        INPUT_FILE
    )

    if len(rtt_values) < 2:
        print(
            "Недостаточно данных для анализа."
        )
        return

    statistics_data = calculate_statistics(
        rtt_values
    )

    variations, average_jitter = (
        calculate_jitter(rtt_values)
    )

    save_statistics(
        statistics_data,
        average_jitter
    )

    plot_rtt(
        sequence_numbers,
        rtt_values
    )

    plot_histogram(
        rtt_values
    )

    plot_jitter(
        sequence_numbers,
        rtt_values,
        variations
    )

    print("Анализ завершён.")
    print()
    print("Статистика RTT:")

    for name, value in statistics_data.items():
        print(
            f"{name}: {value:.3f} мс"
        )

    print(
        f"\nСредний джиттер: "
        f"{average_jitter:.3f} мс"
    )

    print(
        f"\nГрафики и статистика сохранены "
        f"в папке: {RESULTS_DIR}"
    )


if __name__ == "__main__":
    main()