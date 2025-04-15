# Hand Gesture Virtual Keyboard

A computer vision-based virtual keyboard that allows users to type without physical contact using hand gestures captured through a webcam.

![Virtual Keyboard Demo](https://github.com/Jannat20242NSU/User-story/blob/main/keyboard.gif)

## Features

- ✨ Virtual keyboard overlay on webcam feed
- 👆 Type by pointing with index finger
- 👌 Click by bringing index and middle fingers together
- ✊ Pause interaction by making a fist
- ⏱️ Visual feedback with progress indicators for clicks
- ⌨️ A keyboard layout
- 🔙 Backspace and Clear All functionality

## How It Works

This application uses:
- **OpenCV** for webcam capture and image processing
- **MediaPipe** for hand landmark detection and tracking
- Gesture recognition algorithms to interpret hand movements

The system tracks the tip of the index finger to identify which key you're pointing at, and detects when your index and middle fingers come together to register a click.

## Requirements

- Python 3.6+
- Webcam
- Dependencies:
  - OpenCV
  - MediaPipe
  - NumPy

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Jannat20242NSU/hand-gesture-virtual-keyboard.git
cd hand-gesture-virtual-keyboard
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python keyboard.py
```

### Gestures Guide

- **Point**: Move your index finger to the desired key
- **Click**: Bring your index and middle fingers close together and hold briefly
- **Pause**: Make a fist to temporarily pause keyboard interaction
- **Exit**: Press 'q' on your physical keyboard to quit the application

## Customization

You can modify the keyboard layout or adjust sensitivity settings by editing the following variables in the code:

- `keys`: Change the keyboard layout
- `cooldown_time`: Adjust the time between clicks
- `click_animation_duration`: Change how long you need to hold for a click

## Troubleshooting

- **Poor recognition**: Ensure you have adequate lighting
- **Slow performance**: Consider reducing the camera resolution by changing the values in `cap.set()`
- **Hand not detected**: Make sure your hand is clearly visible and within the camera frame

## Future Improvements

- [ ] Add lowercase/uppercase toggle
- [ ] Implement additional gesture shortcuts
- [ ] Optimize for slower systems
- [ ] Add support for special characters
- [ ] Implement word suggestions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe team for their hand tracking solution
- OpenCV community for the computer vision tools
