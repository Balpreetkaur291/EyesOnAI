# EyesOnAI
EyesonAI is a AI-powered accessibility tool designed to assist people with visual impairments by enabling full voice-controlled interaction with their computer. From launching applications to explaining what's on their screen, EyesonAI combines cutting-edge models with system level control to create a seamless and empowering user experience.

<p align="center">
	<img width="500" src="https://github.com/Balpreetkaur291/EyesOnAI/blob/a464a98234220f9ce7c534e1246b421c2c08e090/logo.png">
</p>

# Motivation
Many of us have loved ones family members, friends, and even teachers who live with visual impairments. We noticed that while accessibility tools exist, they are often slow, unintuitive, or difficult to use. With the rapid advancements in AI, we saw an opportunity to reimagine accessibility that is faster, smarter, and more user-centric.

# Implementation
EyesonAI is a AI assistant that listens to user voice commands and performs tasks directly on the computer. It allows users to control system applications (like opening a browser, decreasing the brightness etc.), convert spoken commands to text and reply with speech, read out content using OCR (optical character recognition), handle interactive tasks with contextual awareness using an LLM
Our app runs entirely on the user's local machine and includes a Flask-based local web server. We built the application primarily in Python, using Flask for the UI, LMNT for text-to-speech, Google's Imagen 4 for optical character recognition, and Claude Anthropic 4 as our core large language model. For voice-based interactions, we integrated VAPI to enable AI-driven phone calls. Additionally, we empowered the LLM with access to custom system control scripts, along with visually appealing overlays to enhance usability.

# Installation
To get the project up and running locally, follow these steps:

**Prerequisites**
- Python for the backend

**Clone the Repository**
```
git clone https://github.com/Balpreetkaur291/EyesOnAI
```
**Install dependencies** 
Install the Python dependencies:
```
pip install -r requirements.txt
```
**Start the app**
```
python app.py
```
Open the frontend application in a browser at http://localhost:5000

**Hotkeys**
```
ctrl + space toggles the voice commands
```
This activates voice input mode, allowing you to speak commands directly to your computer. You can control applications, perform searches, interact with files, or even make outbound AI-powered voice calls using VAPI. It’s designed to give users complete voice control over their environment from system-level actions to real-time conversations with a large language model.

# Challenges
Building this system wasn’t straightforward. We faced challenges in setting up and integrating various AI tools, debugging local APIs, and connecting everything into a single functional system. Since our tech stack didn’t follow any traditional template, we had to figure out many things from scratch. Despite all the challenges, we’re incredibly proud of what we’ve built. At the beginning, we weren’t even sure if this project was feasible within our timeline. But not only did we finish it, we built something that we believe can genuinely make life easier for those who are visually impaired. 

# Future Directions
Looking forward, we want to give our assistant deeper control over the system. For example, using OCR to detect screen elements at the pixel level and allowing the AI to interact with more parts of the UI. We hope to expand the range of commands and potentially support offline capabilities in the future. Our ultimate goal is to make Eyes on AI not just a tool, but a trusted companion for visually impaired users navigating the digital world.

