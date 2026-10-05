import socket
import json
import time
import csv


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

MEASUREMENTS_COUNT = 1000
TIMEOUT = 2.0

OUTPUT_FILE = "rtt_results.csv"


def measure_rtt(client_socket, sequence_number):
    message = {
        "sequence_number": sequence_number
    }

    data = json.dumps(message).encode("utf-8")

    send_time = time.perf_counter_ns()

    client_socket.sendto(
        data,
        (SERVER_HOST, SERVER_PORT)
    )

    response_data, _ = client_socket.recvfrom(
        4096
    )

    receive_time = time.perf_counter_ns()

    response = json.loads(
        response_data.decode("utf-8")
    )

    rtt_ms = (
        receive_time - send_time
    ) / 1_000_000

    return {
        "sequence_number": sequence_number,
        "send_time": send_time,
        "server_receive_time": (
            response["server_receive_time"]
        ),
        "receive_time": receive_time,
        "rtt_ms": rtt_ms
    }


def main():
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    client_socket.settimeout(TIMEOUT)

    results = []

    print(
        f"Начало измерений: "
        f"{MEASUREMENTS_COUNT} пакетов"
    )

    for sequence_number in range(
        1,
        MEASUREMENTS_COUNT + 1
    ):
        try:
            result = measure_rtt(
                client_socket,
                sequence_number
            )

            results.append(result)

            print(
                f"Измерение {sequence_number}: "
                f"RTT = {result['rtt_ms']:.3f} мс"
            )

        except socket.timeout:
            print(
                f"Измерение {sequence_number}: "
                f"тайм-аут"
            )

        except (json.JSONDecodeError, KeyError):
            print(
                f"Измерение {sequence_number}: "
                f"некорректный ответ"
            )

    client_socket.close()

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "sequence_number",
                "send_time",
                "server_receive_time",
                "receive_time",
                "rtt_ms"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print("Измерения завершены.")
    print(
        f"Успешных измерений: {len(results)}"
    )
    print(
        f"Результаты сохранены в {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()