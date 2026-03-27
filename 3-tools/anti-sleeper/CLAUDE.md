# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A minimal macOS/desktop utility that prevents the system from sleeping by periodically moving the mouse in small random increments. Built with `tkinter` (GUI) and `pyautogui` (mouse control).

## Running

```bash
python anti-sleeper.py
```

## Dependencies

- `pyautogui` — install via `pip install pyautogui`
- `tkinter` — bundled with standard Python

## Architecture

Single-file app (`anti-sleeper.py`). The `AntiSleepApp` class manages:
- A `tkinter` GUI with Start/Stop buttons
- A daemon `Thread` running `move_mouse()` in the background
- A `threading.Event` (`stop_event`) to signal the thread to halt

Mouse movement runs every 10 seconds, shifting position by ±5px in x and y.
