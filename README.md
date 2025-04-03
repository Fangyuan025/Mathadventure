# 🧮 Math Adventure Game

**Math Adventure** is an educational mini-game that combines math quizzes with RPG-style battles.  
Players answer math questions to defeat monsters across multiple levels, each with unique backgrounds and effects.

---

## Features

- **Interactive Map**: Click on any of the 5 level icons to start battles
- **Turn-based Combat**: Defeat regular monsters and face off against bosses
- **Attack Animations**: Projectile-style effects animate attacks hitting monsters
- **Local LLM Tutor Integration**:
  - If a player answers incorrectly, the question and answer are sent to a local LLM
  - The LLM provides a brief English explanation to help learning
- **Dynamic Battle Backgrounds**: Each level has a distinct environment like forest, volcano, snow, etc.

---

## Controls

| Key       | Action                     |
|-----------|----------------------------|
| ← / →     | Move player left/right     |
| SPACE     | Start input / Next question|
| ENTER     | Submit answer              |
| BACKSPACE | Delete input character     |
| Mouse     | Click to select level      |

---

## Installation

Make sure you have Python (3.10+ recommended) installed. Then run:

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
python game.py
```

---

## Local LLM Integration

This project uses [`microsoft/phi-1_5`](https://huggingface.co/microsoft/phi-1_5) as the default feedback model.  
When a wrong answer is given, the model explains the mistake in a short sentence.

> The model is downloaded automatically from Hugging Face on first use.

GPU acceleration is used if available:

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
```

Alternative models like `TinyLlama`, `Qwen`, or `Mistral` can be configured in `local_llm.py`.

---

## Project Structure

```
MathAdventure/
│
├── game.py               # Main game logic
├── player.py             # Player class
├── monster.py            # Monster class (with HP and boss logic)
├── question.py           # Math question generator
├── local_llm.py          # Local LLM pipeline logic
├── utils.py              # Helpers (text rendering, sounds)
├── FeedbackManager.py    # Feedback text state manager
├── AttackEffect.py       # Attack animation handling
│
├── assets/               # Backgrounds, sprites, and effects
├── requirements.txt      # Python dependencies
```

---

## Example Feedback

> If you answer `1` to `18 + 4 = ?`, the game may show:

```
The student's answer is wrong because they did not carry over the 1 to the next column.
```

---

## Developer Notes

- All assets are loaded from the `assets/` folder
- The game runs fully offline after model is downloaded
- Great for educational projects and kids learning basic arithmetic

---

Enjoy math and monsters!