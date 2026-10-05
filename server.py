import socket
import json
import time


HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 4096


def main():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    server_socket.bind((HOST, PORT))

    print(f"UDP-сервер запущен на {HOST}:{PORT}")

    while True:
        data, client_address = server_socket.recvfrom(
            BUFFER_SIZE
        )

        server_receive_time = time.perf_counter_ns()

        try:
            message = json.loads(
                data.decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

        message["server_receive_time"] = (
            server_receive_time
        )

        response = json.dumps(message).encode(
            "utf-8"
        )

        server_socket.sendto(
            response,
            client_address
        )


if __name__ == "__main__":
    main()