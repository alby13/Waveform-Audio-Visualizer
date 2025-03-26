# Waveform Audio Visualizer

Welcome to the **Waveform Audio Visualizer**! This program visualizes audio input in real-time, displaying the waveform of the audio signal in a graphical window. It uses Python libraries such as `sounddevice`, `numpy`, and `pygame` to capture audio data and render the waveform.

## Features

- Real-time audio visualization
- Interactive audio device selection
- Color-coded waveform based on audio intensity
- Adjustable parameters for sample rate and chunk size

## Requirements

To run this program, you need to have the following Python packages installed:

- `sounddevice`
- `numpy`
- `pygame`

You can install these packages using pip:

```bash
pip install sounddevice numpy pygame
```
<br>

1. Clone the repository

```bash
git clone https://github.com/alby13/Waveform-Audio-Visualizer.git
cd Waveform-Audio-Visualizer
```

2. Run the program:

```bash
python waveform.py
```

3. You can list available audio devices by running

```bash
python waveform.py --list-devices
```

4. To select a specific audio device, run:

```bash
python waveform.py --select-device
```

## Configuration
You can customize the following parameters in the waveform.py file:

<code>DEVICE_ID</code>: Set to None for the default input device or specify a device ID.

<code>SAMPLE_RATE</code>: The number of samples per second (default is 44100 Hz).

<code>CHUNK_SIZE</code>: The number of audio frames per buffer (default is 1024).

<code>WIDTH and HEIGHT</code>: Dimensions of the Pygame window.

<code>BACKGROUND_COLOR</code>: Color of the background (default is black).

<code>LINE_THICKNESS</code>: Thickness of the waveform line.

<code>COLOR_THRESHOLDS_DB</code>: dBFS thresholds for color mapping.

<code>COLOR_PALETTE</code>: List of colors for the waveform based on intensity.

## How It Works
The program captures audio input using the sounddevice library and processes it in chunks. The RMS (Root Mean Square) level of the audio signal is calculated to determine the intensity, which is then mapped to a color from a predefined palette. The waveform is drawn using pygame, updating in real-time as audio data is received.

## Troubleshooting
If you encounter issues, consider the following:

Ensure the correct audio device is selected.
Check if another application is using the audio device.
Verify that the device supports the selected sample rate.
Make sure you have the necessary permissions to access the microphone.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- sounddevice for audio input handling.
- numpy for numerical operations.
- pygame for graphical rendering.
