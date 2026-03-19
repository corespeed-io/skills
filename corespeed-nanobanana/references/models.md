# Supported Gemini Models

## Image Generation

| Model | Best For | Modalities |
|-------|----------|------------|
| `gemini-2.5-flash-image` | Fast image generation + editing, text rendering | IMAGE, TEXT |
| `gemini-2.5-flash` | Text-only tasks, analysis, coding | TEXT |
| `gemini-2.5-flash-lite` | Lightweight text tasks, fastest | TEXT |
| `gemini-2.5-pro` | Complex reasoning, highest quality text | TEXT |

## Model Details

### gemini-2.5-flash-image (default)
- **Image generation** from text prompts
- **Image editing** with input images
- **Multi-image** input support
- **Text rendering** in generated images
- Supports `responseModalities: ["IMAGE", "TEXT"]`

### gemini-2.5-flash
- Fast general-purpose model
- Text and vision (image understanding)
- Cannot generate images (text output only)

### gemini-2.5-pro
- Most capable reasoning model
- Best for complex analysis and long documents
- Text output only

### gemini-2.5-flash-lite
- Fastest and cheapest
- Good for simple tasks
- Text output only

## Response Modalities

| Modality | Description |
|----------|-------------|
| `IMAGE` | Model returns inline image data (base64 PNG/JPEG) |
| `TEXT` | Model returns text |
| `IMAGE, TEXT` | Model may return both images and text captions |

Only `gemini-2.5-flash-image` supports `IMAGE` modality output.
