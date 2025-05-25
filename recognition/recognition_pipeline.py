import io
import os
import shutil
import tempfile

import librosa
import noisereduce as nr
import numpy as np
import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.audio import AudioFile
from demucs.pretrained import get_model
from faster_whisper import WhisperModel
from mir_eval.separation import bss_eval_sources
from pydub import AudioSegment
from pydub.effects import normalize


class AudioTranscriber:
    def __init__(self, work_dir="output", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.work_dir = work_dir
        self._prepare_directory()

    def _prepare_directory(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir, exist_ok=True)

    def channel_dubl(self, input_data: bytes):
        output_path = os.path.join(self.work_dir, "converted.wav")
        sound = AudioSegment.from_file(io.BytesIO(input_data)).set_channels(2).set_frame_rate(44100)
        sound.export(output_path, format="wav")
        return output_path

    def separate_vocals(self, input_path):
        output_path = os.path.join(self.work_dir, "vocals.wav")
        model = get_model(name="htdemucs").to(self.device)
        with tempfile.TemporaryDirectory() as tmpdir:
            wav = AudioFile(input_path).read(streams=0, samplerate=44100)
            sources = apply_model(model, wav[None], device=self.device, split=True, progress=False)
            vocals = sources[0][3]  # vocals
            sf.write(output_path, vocals.T, 44100)
        return output_path

    def enhance_audio(self, input_path, sample_rate=44100, chunk_duration=10):
        output_path = os.path.join(self.work_dir, "enhanced.wav")
        audio, sr = sf.read(input_path)
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        chunk_size = chunk_duration * sample_rate
        enhanced_chunks = []
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            try:
                clean_chunk = nr.reduce_noise(y=chunk, sr=sr, prop_decrease=0.9)
            except Exception as e:
                print(f"⚠️ Ошибка в чанке {i // chunk_size}: {e}")
                clean_chunk = chunk
            enhanced_chunks.append(clean_chunk)
        enhanced_audio = np.concatenate(enhanced_chunks)
        sf.write(output_path, enhanced_audio, sample_rate)
        return output_path

    def postprocess_audio(self, input_path):
        output_path = os.path.join(self.work_dir, "vocal_boosted.wav")
        audio = AudioSegment.from_file(input_path)
        audio = normalize(audio).high_pass_filter(100).low_pass_filter(10000)
        audio += 4
        audio = audio.compress_dynamic_range(threshold=-20.0, ratio=5.0)
        audio.export(output_path, format="wav")
        return output_path

    def transcribe_faster_whisper(self, input_path):
        model = WhisperModel("large-v2", device=self.device)
        print("🎙️ Распознавание с FasterWhisper...")
        segments, _ = model.transcribe(input_path, language="ru")
        return " ".join([seg.text.strip() for seg in segments])

    def test_vocals(self, ref_path, pred_path):
        print(f"Сравнение: {ref_path} vs {pred_path}")
        ref, _ = librosa.load(ref_path, sr=44100, mono=True)
        pred, _ = librosa.load(pred_path, sr=44100, mono=True)
        min_len = min(len(ref), len(pred))
        ref, pred = ref[:min_len], pred[:min_len]
        sdr, sir, sar, _ = bss_eval_sources(np.expand_dims(ref, 0), np.expand_dims(pred, 0))
        print(f"SDR: {sdr[0]:.2f} dB, SIR: {sir[0]:.2f} dB, SAR: {sar[0]:.2f} dB")

    def process(self, input_data) -> str:
        print("🎧 Подготовка канала...")
        path = self.channel_dubl(input_data)

        print("🔍 Выделение вокала...")
        vocals_path = self.separate_vocals(path)
        # self.test_vocals(path, vocals_path)

        print("🧼 Улучшение качества...")
        enhanced_path = self.enhance_audio(vocals_path)

        print("🎚️ Финальная обработка...")
        final_path = self.postprocess_audio(enhanced_path)
        # self.test_vocals(vocals_path, final_path)

        print("📝 Распознавание...")
        text = self.transcribe_faster_whisper(final_path)
        return text


if __name__ == "__main__":
    pipeline = AudioTranscriber(work_dir="temp_output")
    text = pipeline.process("src/Баксанская.wav")
    print("\n📄 Результат распознавания:\n", text)
