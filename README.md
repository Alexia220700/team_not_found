# ChessBot
### Arduino Uno Q + Smartphone Vision System

---

## Project Description

This project is a robotic arm that plays chess autonomously. It uses an Arduino Uno Q to control servo motors and a smartphone camera to detect the chessboard state. The system analyzes the opponent's move, calculates the best response, and physically moves the chess pieces on the board.

The phone acts as a vision system, while the Arduino controls the robotic arm movements.

---

## How It Works

1. The opponent makes a move on the physical chessboard.
2. The smartphone camera captures the chessboard from an overhead position.
3. The computer processes the image and detects the new board state using OpenCV.
4. A chess engine calculates the best move based on the current position.
5. The move is sent to the Arduino via serial communication.
6. The robotic arm executes the move on the physical board by:
   - Moving to the source square
   - Picking up the piece
   - Moving to the destination square
   - Releasing the piece

---

## Hardware Components

| Component | Description |
|-----------|-------------|
| Arduino Uno Q | Main microcontroller (Linux + AI) |
| Robotic Arm | 4–6 DOF servo-based arm |
| Stepper Motors | For base |
| Servo Motors | For elbow and gripper |
| External Power Supply | 5–6V for servos (separate from Arduino) |
| Smartphone | Used as overhead camera |
| USB Cable | Arduino ↔ Computer communication |
| Breadboard & Jumper Wires | For connections |
| Chessboard & Pieces | Standard size recommended |

---

## System Architecture

### Vision System (Smartphone)
- Phone mounted above the chessboard
- Streams or captures images of the board
- Image processing detects piece positions using color/shape detection

### Chess Engine (Computer)
- Converts board state into chess notation (FEN)
- Computes the best move using chess engine logic
- Sends move coordinates (e.g., `E2E4`) to Arduino via Serial

### Robotic Arm Control (Arduino)
- Receives move commands via Serial
- Converts board coordinates (e.g., E2) into servo angles
- Controls arm sequence:
  - Move to source square
  - Lower arm + close gripper
  - Lift arm
  - Move to destination square
  - Lower arm + open gripper
  - Return to standby position

---

## Software Requirements

### Arduino
- Arduino App Lab

### Python 
- OpenCV (`opencv-python`)
- python-chess
- pyserial
- numpy

Install Python dependencies:
pip install opencv-python python-chess pyserial numpy
```bash
pip install opencv-python python-chess pyserial numpy
