# Caesar's Automation Folder

In this larger repo folder I hope to add some projects & files that will go some way to automating me, my thoughts and my voice. See it more as an experiment in how much of myself I can duplicate. It is partly based and inspired on the repo by [Sascha Heyer](https://github.com/SaschaHeyer). 

## Project 1: Voice Synthesis & Story Generation
The first project that you will find in this repo is related to voice synthesis and story generation. Mainly because my girlfriend likes to listen to stories/podcasts but doesn't necessarily like the current voices available (looking at you *The Economist* 😉). So I thought I would try to create a project that could generate stories or take the text from the articles and then read them out in a voice that she prefers.

This project automates the generation of audio stories using AI models and text-to-speech services. It uses Google Cloud's Text-to-Speech, ElevenLabs for the custom voices, and Vertex AI to create stories/other text generation features. 

## Features

- **Story Generation**: Uses Vertex AI to generate story content based on a given prompt.
- **Text-to-Speech Conversion**: Converts generated text into audio using ElevenLabs and Google Cloud's Text-to-Speech.
- **Multi-Speaker Support**: Supports multi-speaker audio synthesis using Google Cloud's beta features.
- **AWS Polly Integration**: Optionally use AWS Polly for text-to-speech synthesis.
- **Streamlit Interface**: Provides a web interface for generating and downloading audio stories.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/REPO_NAME.git
   cd REPO_NAME
   ```

2. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root directory and add your API keys and other environment variables:
   ```plaintext
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   GOOGLE_APPLICATION_CREDENTIALS=path_to_your_google_credentials.json
   ```

## Usage

### Running the Streamlit App

To start the Streamlit app, run:
```bash
streamlit run app.py
```

### Command-Line Interface

You can also generate audio using the command-line interface:
```bash
python generate.py --synthesis_mode default
```

### Options

- `--synthesis_mode`: Choose between `default`, `multispeaker`, or `polly` for different synthesis modes.
- `--use_bedrock`: Use Amazon Bedrock with Anthropic for conversation generation.

## Contributing

Contributions to replace me are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments of tools

- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech)
- [ElevenLabs](https://www.elevenlabs.com/)
- [Vertex AI](https://cloud.google.com/vertex-ai)
- [AWS Polly](https://aws.amazon.com/polly/)
