from pathlib import Path

import numpy as np

from receipt.config import SAMPLE_RATE

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".opus", ".webm"}


def load_audio(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el audio: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato no soportado: {path.suffix}. Usa {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
    import av

    resampler = av.AudioResampler(format="flt", layout="mono", rate=SAMPLE_RATE)
    chunks = []
    try:
        with av.open(str(path)) as container:
            for frame in container.decode(audio=0):
                for resampled in resampler.resample(frame):
                    chunks.append(resampled.to_ndarray().reshape(-1))
            for resampled in resampler.resample(None):
                chunks.append(resampled.to_ndarray().reshape(-1))
    except av.error.FFmpegError as error:
        raise ValueError(f"No se pudo leer el audio {path.name}: {error}") from error
    if not chunks:
        raise ValueError(f"El audio {path.name} no contiene sonido")
    return np.concatenate(chunks).astype(np.float32)
