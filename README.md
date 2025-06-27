# 🧠 Hacking Minigame

A modular terminal-based hacking minigame designed for narrative or immersive use (e.g. LARP, escape games, ARGs, RPGs).  
Players must discover the correct command sequence under pressure, while managing errors and a global timer.

---

## 🎮 Gameplay Overview

- 🧩 The player must input **8 correct commands**, in the correct order.
- ❌ Every **incorrect command** adds +1 to the error count.
- 🔥 At **3 errors**, an alarm is triggered and the game locks for 5 minutes.
- ⏱️ A timer is active during the game to add pressure and realism.
- 💬 The command `help` can be used anytime without penalty.

---

## ⚙️ Configuration

All gameplay parameters are handled through a **separate JSON file**:

- List of **available commands** with descriptions.
- The **target command sequence** to solve the minigame.
- Timer values, error thresholds, messages, etc.

This allows quick and easy reconfiguration depending on the scenario.

---

## ✅ Features

- Modular and readable Python structure.
- Easy to expand with UI or sound triggers (alarm, terminal effects).
- External JSON config — no code modification required for gameplay tweaks.
- Handles command validation, error tracking, progression feedback.

---

## 🚀 Coming Soon

- Admin-only override/reset command.
- Optional sound/QR trigger when the game is solved.
- Web-based version (for touchscreen / kiosk-like setup).
- Logging system (timestamped command history).
- Multiple difficulty profiles.

---

## 📂 File Structure

```bash
📁 Hacking Minigame/
 ├── hack_game.py          # Main game logic
 ├── settings.json         # Global settings (timers, messages, etc.)
 └── commands.json         # All available commands + solution sequence