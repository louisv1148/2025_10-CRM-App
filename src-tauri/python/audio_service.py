"""
Audio recording service for meeting capture
Supports both system audio and microphone input
"""

import pyaudio
import wave
import os
from datetime import datetime
from typing import Optional


class AudioRecorder:
    """Handle audio recording for meetings"""

    def __init__(self, output_dir: str = "../../db/recordings"):
        self.output_dir = output_dir
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.frames = []

        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def list_devices(self):
        """List available audio input devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        return devices

    def start_recording(self, device_index: Optional[int] = None):
        """Start recording audio from specified device"""
        if self.recording:
            raise RuntimeError("Already recording")

        self.frames = []
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk
        )

        self.recording = True
        print(f"Recording started on device {device_index or 'default'}")

    def stop_recording(self) -> str:
        """Stop recording and save to file"""
        if not self.recording:
            raise RuntimeError("Not currently recording")

        self.recording = False
        self.stream.stop_stream()
        self.stream.close()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_{timestamp}.wav"
        filepath = os.path.join(self.output_dir, filename)

        # Save recording
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        print(f"Recording saved to: {filepath}")
        return filepath

    def record_chunk(self):
        """Record a chunk of audio (called in loop during recording)"""
        if self.recording and self.stream:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()


# API endpoint helpers
def get_available_devices():
    """Get list of available recording devices"""
    recorder = AudioRecorder()
    devices = recorder.list_devices()
    recorder.cleanup()
    return devices


def record_meeting(duration: Optional[int] = None, device_index: Optional[int] = None) -> str:
    """
    Record a meeting

    Args:
        duration: Recording duration in seconds (None for manual stop)
        device_index: Audio device to use (None for default)

    Returns:
        Path to saved recording
    """
    recorder = AudioRecorder()

    try:
        recorder.start_recording(device_index=device_index)

        if duration:
            # Record for specified duration
            import time
            for _ in range(0, int(duration * recorder.rate / recorder.chunk)):
                recorder.record_chunk()
        else:
            # Manual recording (controlled by start/stop endpoints)
            pass

        filepath = recorder.stop_recording()
        return filepath

    finally:
        recorder.cleanup()


if __name__ == "__main__":
    # Test audio devices
    print("Available audio input devices:")
    devices = get_available_devices()
    for dev in devices:
        print(f"  [{dev['index']}] {dev['name']} - {dev['channels']} channels @ {dev['sample_rate']} Hz")
