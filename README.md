# 🌌 AntherOS Create (ICLI)

**The Official Interactive Build System for AntherOS Technologies.**

AntherOS Create is a high-performance, single-file build engine designed to transform a base Pop!_OS ISO into **AntherOS**—a gaming-focused, performance-tuned Linux distribution. This tool automates the extraction, "Antherization" (branding & package injection), and high-compression repacking of the OS.

---

## 🚀 Features

- **Infused Scripting:** Core OS customizations are hardcoded into the engine for 1:1 build reproducibility.
- **Dynamic Discovery:** Automatically locates the `filesystem.squashfs` regardless of base ISO versioning.
- **Gaming-Ready:** Injects Steam, Lutris, Gamemode, and 32-bit architecture support out of the box.
- **Live Terminal Logging:** Streams build progress directly to your CLI with real-time feedback.
- **Ownership Correction:** Automatically returns ISO ownership to the non-root user post-build.

---

## 🛠️ Build Requirements

Before running the builder, ensure your host system has the following dependencies:

```
sudo apt update && sudo apt install p7zip-full squashfs-tools xorriso wget -y
```
## 🏗️ How to Build AntherOS
1. Clone the Repository:

  ```
  git clone [https://github.com/anagh9090/AntherOSCreate.git](https://github.com/anagh9090/AntherOSCreate.git)
  cd AntherOSCreate
  ```
2. Prepare Branding (Optional)

3. Launch the Engine:

  ```
  sudo python3 main.py
  ```
4. Interactive Step:
The builder will pause after customization. You can inspect the root filesystem at `./anther_work/squashfs-root/` before pressing Enter to begin the final compression.

## ⚖️ License
Distributed under the **MIT License**. See `LICENSE` for more information.

## 👤 Author
**Anagh** *Founder & CEO, AntherOS Technologies* [GitHub](https://github.com/anagh9090/) | [Website](https://antheros.in/)

*"Building the future of Linux gaming, one block at a time."*
