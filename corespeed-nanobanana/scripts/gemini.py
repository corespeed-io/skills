#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
# ]
# ///
"""
Gemini image & text generation via Google AI Studio through Corespeed AI Gateway.

Requires environment variables:
  CS_AI_GATEWAY_BASE_URL  — AI gateway base URL (e.g. https://gateway.ai.c7d.dev)
  CS_AI_GATEWAY_API_TOKEN — API token for the gateway

Usage:
    uv run gemini.py --prompt "a fox in the forest" -f fox.png
    uv run gemini.py --prompt "a fox in the forest" -f fox.png --model gemini-2.5-flash-image
    uv run gemini.py --prompt "describe this image" -f description.txt -i photo.jpg
    uv run gemini.py --prompt "edit: make the sky purple" -f edited.png -i original.png
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types


def get_mime_type(filepath: str) -> str:
    """Guess MIME type from file extension."""
    mt, _ = mimetypes.guess_type(filepath)
    return mt or "application/octet-stream"


def main():
    parser = argparse.ArgumentParser(
        description="Gemini image & text generation via Corespeed AI Gateway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument("--input", "-i", action="append", dest="inputs", metavar="FILE",
                        help="Input image file(s). Repeat for multiple.")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash-image",
                        help="Model name (default: gemini-2.5-flash-image)")
    parser.add_argument("--modalities", default="auto",
                        help="Response modalities: auto, image, text, image+text")

    args = parser.parse_args()

    # Validate credentials
    base_url = os.environ.get("CS_AI_GATEWAY_BASE_URL", "")
    api_token = os.environ.get("CS_AI_GATEWAY_API_TOKEN", "")

    if not base_url or not api_token:
        print("Error: CS_AI_GATEWAY_BASE_URL and CS_AI_GATEWAY_API_TOKEN environment variables are required.", file=sys.stderr)
        sys.exit(1)

    # Configure Google GenAI client to use gateway
    # The SDK appends /v1beta automatically, so we only need /google-ai-studio
    gateway_url = f"{base_url.rstrip('/')}/google-ai-studio"
    client = genai.Client(
        api_key=api_token,
        http_options=types.HttpOptions(base_url=gateway_url),
    )

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine output type from extension
    out_ext = output_path.suffix.lower()
    is_image_output = out_ext in (".png", ".jpg", ".jpeg", ".webp", ".gif")

    # Determine response modalities
    if args.modalities == "auto":
        if is_image_output:
            response_modalities = ["IMAGE", "TEXT"]
        else:
            response_modalities = ["TEXT"]
    elif args.modalities == "image":
        response_modalities = ["IMAGE"]
    elif args.modalities == "text":
        response_modalities = ["TEXT"]
    else:
        response_modalities = ["IMAGE", "TEXT"]

    # Build content parts
    parts = []

    # Add input images if provided
    if args.inputs:
        for fpath in args.inputs:
            p = Path(fpath)
            if not p.exists():
                print(f"Error: Input file not found: {fpath}", file=sys.stderr)
                sys.exit(1)
            mime = get_mime_type(fpath)
            data = p.read_bytes()
            parts.append(types.Part.from_bytes(data=data, mime_type=mime))
            print(f"Input: {fpath} ({mime}, {len(data)} bytes)")

    # Add text prompt
    parts.append(types.Part.from_text(text=args.prompt))

    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt[:200]}")
    print(f"Modalities: {response_modalities}")
    print("Generating...")

    try:
        response = client.models.generate_content(
            model=args.model,
            contents=types.Content(role="user", parts=parts),
            config=types.GenerateContentConfig(
                response_modalities=response_modalities,
            ),
        )

        if not response.candidates or not response.candidates[0].content.parts:
            print("Error: Empty response from model", file=sys.stderr)
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}", file=sys.stderr)
            sys.exit(1)

        image_count = 0
        text_parts = []

        for i, part in enumerate(response.candidates[0].content.parts):
            if part.inline_data and part.inline_data.data:
                # Save image
                image_data = part.inline_data.data
                mime = part.inline_data.mime_type or "image/png"

                if image_count == 0:
                    save_path = output_path
                else:
                    save_path = output_path.parent / f"{output_path.stem}-{image_count + 1}{output_path.suffix}"

                save_path.write_bytes(image_data)
                full_path = save_path.resolve()
                print(f"\nSaved: {full_path}")
                print(f"MEDIA: {full_path}")
                image_count += 1

            elif part.text:
                text_parts.append(part.text)

        # If no images were generated, save text output
        if image_count == 0 and text_parts:
            text_content = "\n".join(text_parts)
            if is_image_output:
                print("Warning: Model returned text instead of image.", file=sys.stderr)
                print(f"Response: {text_content[:500]}", file=sys.stderr)
                sys.exit(1)
            else:
                output_path.write_text(text_content, encoding="utf-8")
                full_path = output_path.resolve()
                print(f"\nSaved: {full_path}")
                print(f"Text length: {len(text_content)} chars")
        elif text_parts:
            # Print accompanying text
            print(f"\nCaption: {' '.join(text_parts)[:300]}")

        # Print usage
        if response.usage_metadata:
            um = response.usage_metadata
            print(f"Tokens: prompt={um.prompt_token_count}, output={um.candidates_token_count}, total={um.total_token_count}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
