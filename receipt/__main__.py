import argparse


def procesar(audio: str, modo: str = "baseline"):
    return None


def dividir():
    return None


def evaluar(modo: str = "baseline", split: str = "val"):
    return None


def comparar():
    return None


def main():
    parser = argparse.ArgumentParser(prog="receipt")
    sub = parser.add_subparsers(dest="comando")

    p_proc = sub.add_parser("process")
    p_proc.add_argument("audio")
    p_proc.add_argument("--mode", default="baseline")

    p_split = sub.add_parser("split")

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--mode", default="baseline")
    p_eval.add_argument("--split", default="val")

    sub.add_parser("compare")

    args = parser.parse_args()

    if args.comando == "process":
        procesar(args.audio, args.mode)
    elif args.comando == "split":
        dividir()
    elif args.comando == "evaluate":
        evaluar(args.mode, args.split)
    elif args.comando == "compare":
        comparar()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
