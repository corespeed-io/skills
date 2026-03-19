# Gemini API Reference (Google AI Studio via Gateway)

## Endpoint

```
{CS_AI_GATEWAY_BASE_URL}/google-ai-studio/v1beta/models/{model}:generateContent
```

## Authentication

The gateway handles authentication. The script uses `CS_AI_GATEWAY_API_TOKEN` as the API key and routes through `CS_AI_GATEWAY_BASE_URL`.

## generateContent — Request Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contents` | array | ✅ | Array of Content objects |
| `generationConfig` | object | | Generation parameters |
| `safetySettings` | array | | Safety filter settings |

### Content Object

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | `"user"` or `"model"` |
| `parts` | array | Array of Part objects |

### Part Object (input)

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Text content |
| `inlineData` | object | `{"mimeType": "image/png", "data": "<base64>"}` |

### generationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `responseModalities` | array | `["TEXT"]` | `["TEXT"]`, `["IMAGE"]`, or `["IMAGE", "TEXT"]` |
| `temperature` | float | 1.0 | Creativity (0.0–2.0) |
| `topP` | float | 0.95 | Nucleus sampling |
| `topK` | int | 40 | Top-k sampling |
| `maxOutputTokens` | int | 8192 | Max output tokens |
| `candidateCount` | int | 1 | Number of candidates |

## generateContent — Response Schema

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {"text": "..."},
          {"inlineData": {"mimeType": "image/png", "data": "<base64>"}}
        ],
        "role": "model"
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 10,
    "candidatesTokenCount": 100,
    "totalTokenCount": 110
  },
  "modelVersion": "gemini-2.5-flash-image"
}
```

## Examples

### Text-to-Image
```bash
uv run gemini.py --prompt "a watercolor painting of a sunset over mountains" -f sunset.png
```

### Image Editing
```bash
uv run gemini.py --prompt "Remove the background and replace with a beach" -f edited.png -i original.jpg
```

### Image Analysis (text output)
```bash
uv run gemini.py --prompt "Describe this image in detail" -f description.txt -i photo.jpg --model gemini-2.5-flash
```

### Multi-Image Input
```bash
uv run gemini.py --prompt "Combine these two images into one scene" -f combined.png -i image1.png -i image2.png
```

### Text with Custom Model
```bash
uv run gemini.py --prompt "Write a poem about the sea" -f poem.txt --model gemini-2.5-pro
```
