# Ascendio

**Ascendio** is an enchanting endless runner game set in the magical world of Hogwarts. As a young wizard attending the school of witchcraft and wizardry, you must navigate the treacherous Forbidden Forest, dodge dark curses, and collect magical letters to complete powerful spells.

The game features innovative **hand gesture controls** using your webcam, allowing you to cast spells with real hand movements—or play traditionally with your keyboard!

---

## 🎮 Game Story
In the depths of the Forbidden Forest, dark curses have been unleashed...

As a student at Hogwarts, you must master three legendary spells across increasingly difficult challenges:

- **Lumos** - Light in the Darkness (First Year)  
- **Expelliarmus** - The Disarming Charm (Second Year)  
- **Expecto Patronum** - Summon Your Guardian (Third Year)  

Collect golden snitch letters in the correct order to complete each spell while avoiding deadly curse orbs. Only the bravest wizards can master all three challenges!

---

## ✨ Features

### 🎯 Core Gameplay
- **Three Progressive Levels:** Each with unique difficulty and spells to master  
- **Two Control Modes:**  
  - 🤚 Hand Gesture Control (using webcam)  
  - ⌨️ Keyboard Control  
- **Magical Particle Effects:** Stunning visual effects for jumps, collections, and explosions  
- **Dynamic Obstacles:** Cursed orbs with menacing animations  
- **Collectible Letters:** Golden snitch-styled letters that form spell words  
- **Score System:** Earn House Points for dodging obstacles and collecting letters  

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed on your system

### Installation
1. **Clone or download the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/Ascendio.git
cd Ascendio
Install Required Dependencies
bash
pip install pygame opencv-python mediapipe
Or use the requirements file:
bash
pip install -r requirements.txt
Run the Game
bash
python main.py
 Dependencies
pygame (2.0+) - Game engine and graphics
opencv-python (4.5+) - Webcam capture for hand detection
mediapipe (0.8+) - Hand tracking and gesture recognition

🎮 How to Play
🎯 Objective
Complete all three spell challenges by:
Avoiding dark curse orbs that float across the screen
Collecting golden snitch letters in the correct order to spell out magical incantations
Surviving as long as possible to earn maximum House Points
🕹️ Controls
Hand Gesture Mode (Default)
Open Your Hand: Spread 4 or more fingers wide to make your wizard jump
The game uses your webcam to detect hand gestures
Keep your hand visible in the camera frame
Works best with good lighting
Keyboard Mode
SPACE or UP ARROW: Make your wizard jump
H: Switch to Hand Gesture mode
K: Switch to Keyboard mode
ESC: Return to menu or quit game
Universal Controls
Mouse Click: Click buttons on menu screens
ESC: Pause/Return to main menu
🎯 Gameplay Tips
Timing is Everything: Jump at the right moment to avoid curse orbs
Watch the Speed: Each level gets progressively faster
Stay Centered: Don't move too far to the edges
Practice Hand Gestures: In hand mode, quick open-hand gestures work best

📊 Game Progression
Level 1: First Year - LUMOS
Difficulty: Beginner
Spell: Lumos (Light in the Darkness)
Speed: 5
Description: Master the basic light spell
Level 2: Second Year - EXPELLIARMUS
Difficulty: Intermediate
Spell: Expelliarmus (The Disarming Charm)
Speed: 6.5
Description: Learn the duelist's essential charm
Level 3: Third Year - EXPECTO PATRONUM
Difficulty: Advanced
Spell: Expecto Patronum (Summon Your Guardian)
Speed: 8
Description: Call forth your protective Patronus
🏆 Scoring System
Avoid Obstacle: +15 House Points
Collect Letter: +75 House Points
Complete Level: Keep your total score!

🛠️ Technical Details
Hand Detection
Uses MediaPipe Hands for real-time hand tracking
Runs in a separate thread for performance
Detects "open hand" gesture (4+ fingers extended)
Includes debouncing to prevent multiple jumps
Thread-safe jump triggering

<div align="center">
⚡ Ready to Ascend? ⚡
May your spells be powerful and your reflexes swift!
Download Now | View Documentation | Report Bug

Made with 🪄 and ❤️ for the magical community
Star ⭐ this repository if you enjoyed playing Ascendio!
</div>
