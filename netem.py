import argparse
import subprocess
import sys


def run_command(command):
    print(
        "$",
        " ".join(command)
    )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Ошибка:")
        print(result.stderr.strip())
        return False

    if result.stdout.strip():
        print(result.stdout.strip())

    return True


def add_delay(
    interface,
    delay,
    jitter
):
    command = [
        "sudo",
        "tc",
        "qdisc",
        "replace",
        "dev",
        interface,
        "root",
        "netem",
        "delay",
        f"{delay}ms",
        f"{jitter}ms"
    ]

    return run_command(command)


def remove_delay(interface):
    command = [
        "sudo",
        "tc",
        "qdisc",
        "del",
        "dev",
        interface,
        "root"
    ]

    return run_command(command)


def show_delay(interface):
    command = [
        "tc",
        "qdisc",
        "show",
        "dev",
        interface
    ]

    return run_command(command)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Управление искусственной "
            "задержкой через Linux tc/netem"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    add_parser = subparsers.add_parser(
        "add",
        help="Добавить задержку"
    )

    add_parser.add_argument(
        "--interface",
        required=True,
        help="Сетевой интерфейс"
    )

    add_parser.add_argument(
        "--delay",
        type=float,
        required=True,
        help="Средняя задержка, мс"
    )

    add_parser.add_argument(
        "--jitter",
        type=float,
        default=0.0,
        help="Вариация задержки, мс"
    )

    remove_parser = subparsers.add_parser(
        "remove",
        help="Удалить искусственную задержку"
    )

    remove_parser.add_argument(
        "--interface",
        required=True,
        help="Сетевой интерфейс"
    )

    show_parser = subparsers.add_parser(
        "show",
        help="Показать текущие параметры"
    )

    show_parser.add_argument(
        "--interface",
        required=True,
        help="Сетевой интерфейс"
    )

    args = parser.parse_args()

    if args.command == "add":
        success = add_delay(
            args.interface,
            args.delay,
            args.jitter
        )

    elif args.command == "remove":
        success = remove_delay(
            args.interface
        )

    elif args.command == "show":
        success = show_delay(
            args.interface
        )

    else:
        success = False

    sys.exit(
        0 if success else 1
    )


if __name__ == "__main__":
    main()