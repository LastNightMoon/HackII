import os
import shutil
import numpy as np
import soundfile as sf
import librosa
import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize


class AudioProcessor:
    def __init__(self, input_path: str, temp_dir: str = "temp_audio", sample_rate: int = 44100):
        self.input_path = input_path
        self.sample_rate = sample_rate
        self.temp_dir = temp_dir
        self._prepare_temp_dir()

    def _prepare_temp_dir(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
        print(f"Temporary directory '{self.temp_dir}' prepared.")

    def load_audio(self) -> np.ndarray:
        audio, sr = sf.read(self.input_path)
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)  # Convert to mono
        print(f"Loaded audio shape: {audio.shape}, Sample rate: {sr}")
        return audio

    def reduce_noise(self, audio: np.ndarray, chunk_duration: int = 10) -> str:
        chunk_size = self.sample_rate * chunk_duration
        clean_chunks = []

        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            clean_chunk = nr.reduce_noise(y=chunk, sr=self.sample_rate, prop_decrease=0.8)
            clean_chunks.append(clean_chunk)

        clean_audio = np.concatenate(clean_chunks)
        path = os.path.join(self.temp_dir, "clean.wav")
        sf.write(path, clean_audio, self.sample_rate)
        print("Noise reduction complete.")
        return path

    def enhance_vocals(self, path: str, gain_db: float = 6.0) -> str:
        audio = AudioSegment.from_file(path)
        audio = normalize(audio)
        audio = audio.high_pass_filter(100)
        audio = audio.low_pass_filter(10000)
        audio = audio + gain_db
        audio = audio.compress_dynamic_range(threshold=-20.0, ratio=5.0)
        enhanced_path = os.path.join(self.temp_dir, "enhanced.wav")
        audio.export(enhanced_path, format="wav")
        print("Vocal enhancement complete.")
        return enhanced_path

    def pre_emphasis_filter(self, path: str, chunk_duration: int = 10) -> str:
        audio, _ = librosa.load(path, sr=self.sample_rate, mono=True)
        chunk_size = chunk_duration * self.sample_rate
        processed_chunks = []

        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            processed_chunk = librosa.effects.preemphasis(chunk, coef=0.97)
            processed_chunks.append(processed_chunk)

        clean_audio = np.concatenate(processed_chunks)
        output_path = os.path.join(self.temp_dir, "preemphasized.wav")
        sf.write(output_path, clean_audio, self.sample_rate)
        print("Pre-emphasis filtering complete.")
        return output_path

    def final_processing(self, path: str, output_file: str) -> None:
        audio = AudioSegment.from_file(path)
        audio = normalize(audio)
        audio = audio.high_pass_filter(100)
        audio = audio.low_pass_filter(10000)
        audio = audio + 6
        audio = audio.compress_dynamic_range(threshold=-20.0, ratio=6.0)
        audio.export(output_file, format="wav")
        print(f"Final audio saved to {output_file}")

def process_audio(song_path: str, output_path: str = "final_output.wav") -> None:
    processor = AudioProcessor(input_path=song_path)
    raw_audio = processor.load_audio()
    noise_reduced_path = processor.reduce_noise(raw_audio)
    enhanced_path = processor.enhance_vocals(noise_reduced_path)
    preemphasized_path = processor.pre_emphasis_filter(enhanced_path)
    processor.final_processing(preemphasized_path, output_path)


if __name__ == "__main__":
    process_audio("src/Боевая-пехотная.wav")
