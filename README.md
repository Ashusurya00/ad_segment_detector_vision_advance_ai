# 🎯 Ad Segment Detector
### AI-Powered Advertisement Detection and Segmentation System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Multimodal%20AI-purple.svg)]()
[![Machine Learning](https://img.shields.io/badge/ML-Classification-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)]()

## 📌 Overview

**Ad Segment Detector** is an AI-powered multimedia analysis system designed to automatically identify promotional and advertisement-related segments within audio and video content.

The system combines Automatic Speech Recognition (ASR), computer vision, signal analysis, and intelligent scoring techniques to detect promotional content based on multiple contextual signals.

Instead of relying on a single keyword or visual indicator, the system analyzes different sources of information to determine whether a particular segment contains advertising or promotional material.

The objective is to make advertisement identification more intelligent, automated, and context-aware.

## 🎯 Problem Statement

Audio and video content frequently contains advertisements, sponsorship announcements, promotional messages, discount offers, and brand integrations.

Manually identifying these segments is time-consuming and difficult, especially when dealing with lengthy multimedia recordings.

Traditional keyword-based detection systems often fail because:
- Advertisements can be expressed using different languages.
- Promotional messages may not contain predefined keywords.
- Brand promotions can appear through speech, visuals, or both.
- Context is important when distinguishing advertisements from ordinary conversations.
- Advertisements may occur only within specific portions of a video.

### Proposed Solution

We developed a modular AI-based system that:

1. Processes audio and video inputs.
2. Extracts spoken content using ASR.
3. Analyzes visual information using computer vision.
4. Identifies promotional indicators and advertising signals.
5. Calculates confidence scores using a scoring mechanism.
6. Detects and extracts potential advertisement segments with timestamps.

## 🏗️ System Architecture

The project follows a modular multimedia processing pipeline.

```text
             Audio / Video Input
                     |
                     v
              Media Processing
                     |
          +----------+----------+
          |                     |
          v                     v
     Audio Module          Vision Module
          |                     |
          v                     v
     Speech-to-Text       Visual Analysis
          |                     |
          v                     v
     ASR Signals          Visual Signals
          |                     |
          +----------+----------+
                     |
                     v
             Signal Extraction
                     |
                     v
              Scoring Engine
                     |
                     v
             Candidate Detection
                     |
                     v
             Segment Detection
                     |
                     v
           Start / End Timestamps
                     |
                     v
             Final Ad Detection
```

## ⚙️ Core Modules

### 1. Media Processing
- Handles multimedia input.
- Prepares media for audio and visual analysis.
- Supports the processing pipeline.

### 2. Automatic Speech Recognition (ASR)
- Extracts spoken words from audio.
- Generates textual transcripts.
- Identifies promotional phrases and sponsorship-related expressions.
- Supports identifying signals such as:
  - "Sponsored by"
  - "Book now"
  - "Limited-time offer"
  - Promotional announcements.

### 3. Computer Vision Module
- Analyzes visual information from multimedia content.
- Identifies visual indicators associated with promotional content.
- Generates promotional classifications and confidence scores.

### 4. Signal Extraction
The system identifies multiple promotional indicators, including:

| Signal | Description |
|---|---|
| Promotional phrases | Detects advertising-related expressions |
| Sponsorship phrases | Identifies sponsorship announcements |
| Phone numbers | Detects potential business contact information |
| Discount indicators | Identifies offers and promotional discounts |
| Visual signals | Uses visual analysis to identify promotional content |

### 5. Scoring Engine
The scoring module combines different detection signals to determine whether a segment is a potential advertisement.

It considers:
- ASR-based confidence.
- Promotional keyword matches.
- Contact information indicators.
- Discount and offer indicators.
- Visual classification results.

The scoring mechanism helps reduce dependence on individual keywords and supports more contextual decisions.

### 6. Segment Detection
- Identifies potential advertisement intervals.
- Determines segment start and end timestamps.
- Associates confidence scores with detected segments.
- Returns candidate promotional segments for further inspection.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Speech Processing | Automatic Speech Recognition (ASR) |
| Computer Vision | Vision-based classification |
| Multimedia Processing | FFmpeg |
| Data Processing | Python-based signal processing |
| Detection Strategy | Rule-based and confidence-based scoring |
| Testing | Pytest |
| Development Environment | VS Code, Python Virtual Environment |
| Version Control | Git and GitHub |

## 📂 Project Structure

```text
ad-segment-detector/
│
├── app/
│   ├── test_media.py
│   ├── test_asr.py
│   ├── test_vision.py
│   ├── test_scoring.py
│   └── test_segmenter.py
│
├── media/
│   └── Sample audio/video files
│
├── requirements.txt
├── README.md
├── .gitignore
└── main.py
```

*Note: Adjust the directory structure to match the final repository.*

## 🔄 How the System Works

**Step 1: Input Processing**

The system receives multimedia content and prepares it for analysis.

**Step 2: Speech Extraction**

The ASR module converts speech into text and extracts relevant promotional phrases.

**Step 3: Visual Analysis**

The vision module analyzes visual information and produces promotional classification results.

**Step 4: Signal Identification**

The system identifies advertising indicators such as sponsorship phrases, phone numbers, booking instructions, and discounts.

**Step 5: Confidence Scoring**

The scoring engine combines the available signals to calculate an advertisement detection score.

**Step 6: Segment Identification**

The segmenter identifies potential promotional intervals and returns their timestamps and confidence levels.

## 🧪 Testing and Validation

The project includes modular tests to validate individual components.

| Test File | Testing Purpose |
|---|---|
| `test_media.py` | Media processing validation |
| `test_asr.py` | Speech recognition validation |
| `test_vision.py` | Visual analysis validation |
| `test_scoring.py` | Advertisement scoring validation |
| `test_segmenter.py` | Segment detection validation |

Run the test suite:

```bash
pytest app/ -v
```

## 📊 Sample Detection Output

An example from the development testing process:

```text
ASR Score: 0.8

Final Result:
Score: 0.82
Candidate: True

Detected Signals:
- phrase:sponsored by
- phrase:book now
- phone_number
- discount

Segment:
Start: 8.00 seconds
End: 14.00 seconds
Confidence: 0.85
```

<Note>
The values above represent an observed development test result, not a benchmark of overall model accuracy.
</Note>

## 🚀 Installation and Setup

### Prerequisites

- Python 3.11+
- Git
- FFmpeg
- VS Code (recommended)

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ad-segment-detector
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

*Make sure the entry-point filename matches your actual project.*

### 5. Execute Tests

```bash
pytest app/ -v
```

## 💡 Key Engineering Challenges

Some of the major engineering challenges addressed during development include:

1. **Multimodal Analysis:** Combining information from speech and visual content instead of relying on a single detection source.

2. **False Positive Reduction:** Ordinary conversations may contain promotional words. Multiple signals and scoring help improve detection decisions.

3. **Timestamp Accuracy:** Identifying the actual beginning and ending of promotional segments rather than simply classifying an entire video.

4. **Speech Recognition Variability:** Handling inconsistent transcription quality and mixed-language speech.

5. **Modular Development:** Separating media processing, ASR, vision, scoring, and segmentation to simplify debugging, testing, and future improvements.

## 🔮 Future Enhancements

- Deep learning-based advertisement classification.
- Advanced multilingual speech recognition.
- Transformer-based contextual advertisement detection.
- Brand logo and product placement detection.
- Real-time advertisement detection in live streams.
- Improved temporal segmentation.
- Web-based dashboard using Streamlit or FastAPI.
- Model evaluation using precision, recall, F1-score, and IoU.
- Deployment using Docker and cloud infrastructure.

## 🎯 Applications

- YouTube and streaming content analysis.
- Podcast advertisement detection.
- Television broadcast monitoring.
- Sponsorship identification.
- Media content auditing.
- Automated advertisement analytics.

## 👨‍💻 Project Objective

This project demonstrates the practical application of AI/ML engineering concepts in multimedia intelligence, including speech recognition, computer vision, multimodal signal extraction, confidence-based scoring, and temporal segmentation.

The long-term objective is to develop a scalable and reliable advertisement detection solution capable of understanding promotional content across different media formats.

---

**Developed as an AI/ML Engineering Project**

**Technologies:** Python | ASR | Computer Vision | Multimodal AI | Signal Processing | Pytest | FFmpeg

⭐ If you find this project interesting, consider giving the repository a star!
