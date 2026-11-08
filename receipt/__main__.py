import argparse
import json
import sys

from receipt.config import MODES, SPLIT_RATIOS

FIELD_LABELS = [("cliente", "Cliente"), ("producto", "Producto"), ("producto_id", "ID producto"),
                ("cantidad", "Cantidad"), ("medida", "Medida"), ("hora_entrega", "Hora de entrega")]


def print_result(result):
    ticket = result.ticket
    print(f"Transcripción: {result.transcription}")
    for name, label in FIELD_LABELS:
        value = getattr(ticket, name)
        print(f"{label}: {'(vacío)' if value in (None, '') else value}")
    if ticket.review_fields:
        print(f"Por confirmar: {', '.join(ticket.review_fields)}")
    if result.extra_products:
        print(f"Otros productos detectados: {', '.join(result.extra_products)}")
    if result.used_fallback:
        print("AVISO: Ollama no respondió; este ticket salió de las reglas (línea base), no del modelo de lenguaje.")
    print(f"Tiempos: transcripción {result.transcription_seconds:.2f} s, extracción {result.extraction_seconds:.2f} s")


def build_parser():
    parser = argparse.ArgumentParser(prog="receipt", description="Nota de voz a ticket de pedido")
    commands = parser.add_subparsers(dest="command", required=True)
    process = commands.add_parser("process", help="procesa un archivo de audio")
    process.add_argument("audio")
    text = commands.add_parser("text", help="procesa una frase ya transcrita")
    text.add_argument("phrase")
    for command in (process, text):
        command.add_argument("--mode", choices=list(MODES), default="baseline")
    commands.add_parser("split", help="crea data/splits.csv")
    evaluate = commands.add_parser("evaluate", help="evalúa un modo sobre una división")
    evaluate.add_argument("--mode", choices=list(MODES), required=True)
    evaluate.add_argument("--split", choices=list(SPLIT_RATIOS), required=True)
    commands.add_parser("compare", help="tabla Markdown con los resultados guardados")
    return parser


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        if args.command == "process":
            from receipt import pipeline
            print(f"Carga de modelos: {pipeline.load_models(args.mode):.2f} s")
            print_result(pipeline.process_audio(args.audio, args.mode))
        elif args.command == "text":
            from receipt import pipeline
            print_result(pipeline.process_text(args.phrase, args.mode))
        elif args.command == "split":
            from receipt import dataset
            splits = dataset.make_split()
            print(splits["split"].value_counts().to_string())
        elif args.command == "evaluate":
            import torch
            if not torch.cuda.is_available():
                print("ADVERTENCIA: no hay GPU CUDA; la evaluación correrá en CPU y será lenta. "
                      "Los tiempos no son comparables con los de GPU.", file=sys.stderr)
            from receipt import evaluation
            print(json.dumps(evaluation.evaluate(args.mode, args.split), indent=2, ensure_ascii=False))
        else:
            from receipt import evaluation
            print(evaluation.comparison_table())
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
