import sounddevice as sd
import numpy as np
import pygame
import queue
import sys
import math

# --- Configuration ---
DEVICE_ID = None        # None for default input device
SAMPLE_RATE = 44100     # Samples per second (Hz)
CHUNK_SIZE = 1024       # How many audio frames per buffer (smaller for faster wave updates)
WIDTH, HEIGHT = 1000, 500 # Window dimensions
BACKGROUND_COLOR = (0, 0, 0) # Black

# --- Waveform Styling ---
LINE_THICKNESS = 2
# Color mapping based on RMS dBFS level of the chunk
# Lower dB -> Whiter, Higher dB -> Redder
# Adjust thresholds to match your input sensitivity
COLOR_THRESHOLDS_DB = [-45, -30, -15] # dBFS thresholds for White->Yellow, Yellow->Orange, Orange->Red
COLOR_PALETTE = [
    (255, 255, 255), # White
    (255, 255, 0),   # Yellow
    (255, 165, 0),   # Orange
    (255, 0, 0)      # Red
]
# --- End Configuration ---

# --- Global Variables ---
audio_q = queue.Queue() # Thread-safe queue for audio data
latest_data_chunk = np.zeros(CHUNK_SIZE, dtype=np.float32) # Buffer for latest audio data
last_rms_dbfs = -np.inf
new_data_available = False
# ---

def list_audio_devices():
    """Prints available audio devices."""
    print("Available audio devices:")
    print(sd.query_devices())
    sys.exit(0)

def select_device():
    """Interactive selection of audio device."""
    print("Available audio devices:")
    print(sd.query_devices())
    try:
        dev_id = int(input("Enter the device ID you want to use: "))
        sd.check_input_settings(device=dev_id, samplerate=SAMPLE_RATE)
        return dev_id
    except Exception as e:
        print(f"Invalid selection or device error: {e}")
        print("Using default device instead.")
        return None

def audio_callback(indata, frames, time_info, status):
    """This is called (from a separate thread) for each audio block."""
    global new_data_available
    if status:
        print(status, file=sys.stderr)
    # Put the raw audio data onto the queue
    # Using only the first channel
    audio_q.put(indata[:, 0].copy())
    new_data_available = True # Signal that data is ready

def calculate_rms_dbfs(data_chunk):
    """Calculates RMS level in dBFS."""
    epsilon = 1e-10 # Avoid log10(0)
    rms_linear = np.sqrt(np.mean(data_chunk**2))
    rms_dbfs = 20 * np.log10(rms_linear + epsilon)
    return rms_dbfs

def get_waveform_color(rms_dbfs):
    """Maps an RMS dBFS value to a color from the palette."""
    if rms_dbfs < COLOR_THRESHOLDS_DB[0]:
        return COLOR_PALETTE[0] # White
    elif rms_dbfs < COLOR_THRESHOLDS_DB[1]:
        return COLOR_PALETTE[1] # Yellow
    elif rms_dbfs < COLOR_THRESHOLDS_DB[2]:
        return COLOR_PALETTE[2] # Orange
    else:
        return COLOR_PALETTE[3] # Red

def generate_waveform_points(data_chunk, width, height):
    """Generates a list of (x, y) points for drawing the waveform."""
    num_samples = len(data_chunk)
    if num_samples == 0:
        return []

    points = []
    max_amplitude = height / 2  # Max vertical displacement from center
    center_y = height / 2
    x_scale = width / (num_samples - 1) if num_samples > 1 else width

    for i, amplitude in enumerate(data_chunk):
        # Clamp amplitude just in case it exceeds -1.0 to 1.0 slightly
        clamped_amplitude = max(-1.0, min(1.0, amplitude))

        x = int(i * x_scale)
        # Y calculation: Start from center, subtract scaled amplitude (Pygame Y increases downwards)
        y = int(center_y - clamped_amplitude * max_amplitude)
        points.append((x, y))

    # Ensure we always have at least two points to draw lines
    if len(points) == 1:
        points.append(points[0]) # Duplicate the point if only one sample

    return points

# --- Main Execution ---
if __name__ == "__main__":
    if '--list-devices' in sys.argv:
        list_audio_devices()

    if '--select-device' in sys.argv:
        DEVICE_ID = select_device()

    # --- Initialize Pygame ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Live Waveform Visualizer")
    clock = pygame.time.Clock() # To control frame rate (optional)
    # ---

    stream = None # Initialize stream variable
    try:
        # --- Create Audio Stream ---
        stream = sd.InputStream(
            device=DEVICE_ID,
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK_SIZE,
            callback=audio_callback,
            dtype='float32' # Essential for -1.0 to 1.0 range
        )
        stream.start()
        print(f"Starting audio stream from device {DEVICE_ID if DEVICE_ID is not None else 'default'}...")
        print(f"Sample Rate: {SAMPLE_RATE} Hz, Chunk Size: {CHUNK_SIZE} frames")
        print("Close the Pygame window to stop.")
        # ---

        # --- Main Loop ---
        running = True
        while running:
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # ---

            # --- Get Audio Data ---
            if new_data_available:
                try:
                    # Get the most recent chunk
                    while not audio_q.empty(): # Process all waiting chunks, use the last one
                         latest_data_chunk = audio_q.get_nowait()
                    last_rms_dbfs = calculate_rms_dbfs(latest_data_chunk)
                    new_data_available = False # Reset flag
                except queue.Empty:
                    # Should not happen if new_data_available is True, but handle anyway
                    pass
            # ---

            # --- Drawing ---
            screen.fill(BACKGROUND_COLOR) # Clear screen with black

            # Generate points for the current waveform chunk
            waveform_points = generate_waveform_points(latest_data_chunk, WIDTH, HEIGHT)

            # Determine color based on the RMS level of the *current* chunk
            current_color = get_waveform_color(last_rms_dbfs)

            # Draw the waveform lines if we have enough points
            if len(waveform_points) >= 2:
                pygame.draw.lines(screen, current_color, False, waveform_points, LINE_THICKNESS)

            # --- Update Display ---
            pygame.display.flip()
            # ---

            # Optional: Limit frame rate
            # clock.tick(60) # Limit to 60 FPS

        # --- End Main Loop ---

    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if isinstance(e, sd.PortAudioError):
            print("\n>>> Common Issues <<<")
            print("- Is the correct audio device selected? Try '--list-devices' or '--select-device'.")
            print("- Is another application using the audio device?")
            print("- Does the device support the selected sample rate ({SAMPLE_RATE} Hz)?")
            print("- Ensure you have necessary permissions to access the microphone.")
        # Attempt to clean up pygame even on error
        if pygame.get_init():
             pygame.quit()
        sys.exit(1)
    finally:
        # --- Clean Up ---
        if stream is not None and stream.active:
            stream.stop()
            stream.close()
            print("Audio stream stopped.")
        if pygame.get_init():
            pygame.quit()
        print("Exiting.")
