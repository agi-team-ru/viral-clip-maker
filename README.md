# AI Viral Clip Maker

## Overview

Our solution offers an innovative, cost-effective approach to video editing, leveraging AI to automate the process of creating engaging short-form content from longer videos. This tool is particularly valuable for content creators, bloggers, and marketers looking to enhance their social media presence without the high costs associated with traditional video editing services.
[https://demo.agi-team.ru/](url)
## Key Features

- **AI-Driven Scene Selection**: Utilizes advanced algorithms to identify the most engaging parts of a video.
- **Subtitle Generation and Overlay**: Automatically generates and applies subtitles with customizable styles.
- **Face Detection and Tracking**: Employs two models for accurate face detection and movement capture.
- **User Preference Integration**: Allows users to set preferences before content generation.
- **Simple Video and Audio Editor**: Provides basic editing capabilities for final touches.
- **Mobile Support**: Fully functional on mobile devices with an intuitive UI.

 ![image](https://github.com/user-attachments/assets/09050f06-fc1d-42df-b4d3-f5c881879261)


- **Explainable AI**: Offers insights into why specific scenes were selected.
- **Non-Chronological Editing**: Capable of creating clips from various parts of the original video.
- **Dockerized Solution**: Easy to deploy with zero-configuration setup.
- **Lightweight Model**: Uses a small, efficient model suitable for production environments.
- **Airgapped Operation**: No external API dependencies, ensuring data privacy and security.
## Demonstration

Here's an example of a video created by our AI editor:
![Demo](https://github.com/user-attachments/assets/5cfc6ca7-f47f-4d4a-884d-135c62634f4f)
As you can see, our editor automatically:
- Places the main video in the center
- Adds a background image at the top
- Inserts an avatar in the bottom left corner
- Overlays subtitles on the video
  
## Comparative Advantages

### vs. Traditional Editing Services
- **Cost-Effective**: Significantly reduces editing costs compared to hiring professional editors.
- **Time-Efficient**: Automates time-consuming tasks, delivering results faster.
- **Consistency**: Ensures a consistent style across all edited videos.

### vs. Other AI Solutions
- **Comprehensive Analysis**: Unlike some solutions that rely solely on speech, our tool analyzes visual content even in silent scenes.
- **Customizable**: Offers more flexibility in output style and content selection.
- **Privacy-Focused**: Operates without sending data to external services.

## Technical Highlights

1. **Scene Analysis Algorithm**:
   - Utilizes graph-based models for facial movement capture.
   - Employs a separate model for face detection.
   - Analyzes scenes individually before final compilation.
    

2. **Subtitle Overlay Process**:
   - Implements a metered text selection based on timing.
   - Offers customizable fonts and adaptive positioning.
  
![image](https://github.com/user-attachments/assets/0cb4537e-6bd1-456d-a4da-40bdf548b03b)

3. **Image Cropping Process**:
  - Implements precise image area selection based on specified parameters.

![image](https://github.com/user-attachments/assets/fcd01494-6707-4f85-89f7-505710f5dba0)


4. **Whisper Integration**:
   - Separate server setup for Whisper to optimize pipeline performance.

5. **Prompt Engineering**:
   - Utilizes sophisticated prompt engineering techniques to enhance AI performance.

## Challenges Overcome

- Developed solutions for analyzing scenes without speech but with significant visual content.
- Optimized the balance between AI capabilities and processing speed for production use.

## Market Relevance

This solution addresses a growing need in the content creation industry. Many popular bloggers and influencers (e.g., MelStroy, Arsen Markaryan) have historically paid substantial amounts for video editing services. Our tool democratizes this process, making it accessible to creators of all levels.

## Key Insights

- **Virality ≠ Popularity**: Our tool helps create viral-worthy content, but understands that true popularity stems from consistent, quality content.
- **Adaptability**: Suitable for various content types and styles, from educational to entertainment.

## UI

![image](https://github.com/user-attachments/assets/9e9b85fb-63ce-4554-b8d3-19f4e5df5d19)

## Architecture

![image](https://github.com/user-attachments/assets/51124fc0-fce1-417b-ae19-ae48896ed48a)


## Getting Started

Copy file `.env.example` to `.env` and adjust configuration.

Run:

```bash
docker compose up -d --build
```

### VS Code

Install venv:

```bash
cd services/gradio
python -m venv .venv
source .venv/bin/activate
pip install -r ./requirements.txt
```

Run command in VS Code (Press F1): `Python: Select Interpreter`

Enter: `./services/gradio/.venv/bin/python`

### Run tests

Place your sample video to `./samples/test_video1.mp4`

In `services/gradio` run:

```bash
source .venv/bin/activate
pip install python-dotenv==1.0.1
```
# Project Using Whisper Timestamped Server

This project utilizes [whisper-timestamped-server](https://github.com/idashevskii/whisper-timestamped-server) for processing audio with Whisper and obtaining word-level timestamps.

## Installation and Setup

1. Clone the whisper-timestamped-server repository:
   ```
   git clone https://github.com/idashevskii/whisper-timestamped-server.git
   cd whisper-timestamped-server
   ```

2. Launch the server locally using Docker Compose:
   ```
   docker-compose up -d
   ```

3. After successful launch, determine the hostname or IP address on which the server is running.

4. In the `.env` file of your main project, locate the `WHISPER_BASE_URL=` line and replace the value with the address of your locally running server. For example:
   ```
   WHISPER_BASE_URL=http://localhost:9001
   ```
   or
   ```
   WHISPER_BASE_URL=http://192.168.1.100:9001
   ```

5. Save the changes to the `.env` file.

## Usage

Your project is now configured to use the locally running whisper-timestamped-server. You can continue working with your main application, which will communicate with this server for audio processing and timestamp retrieval.



## Note

Ensure that the whisper-timestamped-server is running and accessible before using your main application.
## Acknowlegment

* [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped): Whisper with word-level timestamps (License AGPL-3.0).
* [whisper-timestamped-server](https://github.com/idashevskii/whisper-timestamped-server): Whisper with word-level timestamps (License GPL-3.0).
* [gradio](https://github.com/gradio-app/gradio): Machine Learning Web Apps (License Apache-2.0).
* [vuetify-fastapi-pg-template](https://github.com/idashevskii/vuetify-fastapi-pg-template): Project Template (License MIT).
