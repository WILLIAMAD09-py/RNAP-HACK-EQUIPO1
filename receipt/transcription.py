from __future__ import annotations

DEFAULT_WHISPER = "small"
LANGUAGE = "es"
MUESTRAS_POR_SEGUNDO = 16000


def _cargar_audio(ruta, sample_rate: int = MUESTRAS_POR_SEGUNDO):
    import av
    import numpy as np

    contenedor = av.open(ruta)
    stream = contenedor.streams.audio[0]
    resampler = av.audio.resampler.AudioResampler(
        format="s16", layout="mono", rate=sample_rate
    )
    trozos = []
    for frame in contenedor.decode(stream):
        for out_frame in resampler.resample(frame):
            trozos.append(out_frame.to_ndarray())
    contenedor.close()
    if not trozos:
        return np.zeros(0, dtype=np.float32)
    audio = np.concatenate(trozos, axis=1).ravel().astype(np.float32)
    return audio / 32768.0


class Transcriptor:
    def __init__(self, modelo: str = DEFAULT_WHISPER, idioma: str = LANGUAGE):
        self.modelo = modelo
        self.idioma = idioma
        self._model = None

    def cargar(self):
        if self._model is None:
            import whisper
            self._model = whisper.load_model(self.modelo)
        return self._model

    def transcribir(self, audio) -> str:
        model = self.cargar()
        result = model.transcribe(audio, language=self.idioma, fp16=False)
        return result.get("text", "").strip()


def transcribir_archivo(ruta_audio, modelo: str = DEFAULT_WHISPER) -> str:
    audio = _cargar_audio(ruta_audio)
    transcriptor = Transcriptor(modelo=modelo)
    return transcriptor.transcribir(audio)
