"""
Module for audio recording and speech detection.
"""

import pyaudio
import wave
import numpy as np
import time
from array import array
from threading import Thread, Event
import logging
from utils.config import (
    SAMPLE_RATE, CHANNELS, SILENCE_THRESHOLD,
    SILENCE_DURATION, MIN_PHRASE_DURATION, TEMP_AUDIO_PATH
)
from audio.audio_player import AudioPlayer

logger = logging.getLogger(__name__)

# Constants
MAX_RECORDING_TIME = 5.0  # Maximum time to record after speech is detected
SILENCE_CHUNKS_THRESHOLD = 5  # Number of consecutive silent chunks to consider speech ended
INTERRUPTION_THRESHOLD = 2  # Number of consecutive non-silent chunks to detect interruption
INTERRUPTION_CHECK_INTERVAL = 0.02  # Check for interruptions every 20ms (more frequent)
INTERRUPTION_VOLUME_THRESHOLD = 1000  # Lower threshold for detecting interruptions
PRE_BUFFER_SIZE = 3  # Number of chunks to keep before interruption is detected

class AudioRecorder:
    def __init__(self):
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.silence_threshold = SILENCE_THRESHOLD
        self.silence_duration = SILENCE_DURATION
        self.min_phrase_duration = MIN_PHRASE_DURATION
        self.stop_event = Event()
        self.audio_detected_event = Event()
        self.recording_thread = None
        self.p = None
        self.stream = None
        self.audio_player = AudioPlayer()
        
    def start_listening(self):
        """Start listening for audio in a background thread."""
        if self.recording_thread and self.recording_thread.is_alive():
            logger.warning("Already listening")
            return False
            
        self.stop_event.clear()
        self.audio_detected_event.clear()
        self.recording_thread = Thread(target=self._listen_for_speech)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        logger.info("Started listening for speech")
        return True
        
    def stop_listening(self):
        """Stop the background listening thread."""
        if self.recording_thread and self.recording_thread.is_alive():
            self.stop_event.set()
            self.recording_thread.join(timeout=2.0)
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()
            logger.info("Stopped listening")
            return True
        return False
        
    def wait_for_speech(self, timeout=None):
        """Wait until speech is detected and recorded."""
        return self.audio_detected_event.wait(timeout=timeout)
        
    def _is_silent(self, data_chunk, threshold=None):
        """Check if the audio chunk is below the silence threshold."""
        as_ints = array('h', data_chunk)
        max_amplitude = max(abs(x) for x in as_ints)
        threshold = threshold or self.silence_threshold
        is_silent = max_amplitude < threshold
        logger.debug(f"Audio chunk max amplitude: {max_amplitude}, is_silent: {is_silent}")
        return is_silent
        
    def _listen_for_speech(self):
        """Background thread that listens for speech and records it when detected."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        logger.info("Microphone is open and listening...")
        
        while not self.stop_event.is_set():
            # Check if avatar is speaking
            if self.audio_player.is_playing_audio():
                logger.info("Avatar is speaking, listening for interruptions...")
                non_silent_chunks = 0
                last_check_time = time.time()
                pre_buffer = []
                
                # Listen for potential interruption
                while self.audio_player.is_playing_audio() and not self.stop_event.is_set():
                    current_time = time.time()
                    if current_time - last_check_time >= INTERRUPTION_CHECK_INTERVAL:
                        last_check_time = current_time
                        data = self.stream.read(self.chunk, exception_on_overflow=False)
                        
                        # Keep a rolling buffer of recent audio
                        pre_buffer.append(data)
                        if len(pre_buffer) > PRE_BUFFER_SIZE:
                            pre_buffer.pop(0)
                        
                        if not self._is_silent(data, INTERRUPTION_VOLUME_THRESHOLD):
                            non_silent_chunks += 1
                            logger.debug(f"Non-silent chunk detected: {non_silent_chunks}/{INTERRUPTION_THRESHOLD}")
                            if non_silent_chunks >= INTERRUPTION_THRESHOLD:
                                logger.info("User interruption detected, stopping avatar speech")
                                self.audio_player.stop_audio()
                                break
                        else:
                            non_silent_chunks = 0
                    time.sleep(0.005)  # Reduced sleep time for more responsive checking
                    
                # If we stopped the avatar, start recording the user's speech
                if not self.audio_player.is_playing_audio():
                    logger.info("Starting to record user's interruption")
                    # Start with the pre-buffer content to capture the beginning of the interruption
                    self._record_speech(pre_buffer)
                    continue
            
            # Normal speech detection
            silent_chunks = 0
            speech_detected = False
            
            while not speech_detected and not self.stop_event.is_set():
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                if not self._is_silent(data):
                    speech_detected = True
                    logger.info("Speech detected, recording...")
                    break
                    
            if not speech_detected:
                continue
                
            # Record the speech
            self._record_speech()
                
    def _record_speech(self, initial_frames=None):
        """Record speech until silence or timeout is detected."""
        frames = initial_frames or []
        recording_start_time = time.time()
        silent_chunks = 0
        recording_active = True
        
        while recording_active and not self.stop_event.is_set():
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)
            
            # Check for silence
            if self._is_silent(data):
                silent_chunks += 1
                if silent_chunks >= SILENCE_CHUNKS_THRESHOLD:
                    logger.info("Silence detected, stopping recording")
                    recording_active = False
            else:
                silent_chunks = 0
            
            # Check if we've reached the maximum recording time
            if time.time() - recording_start_time >= MAX_RECORDING_TIME:
                logger.info(f"Maximum recording time ({MAX_RECORDING_TIME}s) reached")
                recording_active = False
                
        recording_duration = time.time() - recording_start_time
        
        if recording_duration < self.min_phrase_duration:
            logger.info(f"Speech too short ({recording_duration:.2f}s), ignoring")
            return
            
        # Save the recorded audio to a file
        self._save_audio(frames)
        logger.info(f"Recording saved ({recording_duration:.2f}s)")
        
        # Signal that audio is ready for processing
        self.audio_detected_event.set()
        
        # Wait for the event to be cleared before continuing to listen
        while self.audio_detected_event.is_set() and not self.stop_event.is_set():
            time.sleep(0.1)
                
    def _save_audio(self, frames):
        """Save recorded audio frames to a WAV file."""
        with wave.open(TEMP_AUDIO_PATH, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            
    def reset_detection_event(self):
        """Reset the audio detection event to listen for new speech."""
        self.audio_detected_event.clear()
