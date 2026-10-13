#!/usr/bin/env python3
"""
Mondo Style Design Generator - Enhanced Version
Features: AI prompt optimization, 3-column comparison, image-to-image, 20 artist styles
"""

import os
import sys
import argparse
import requests
import base64
import json
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# API Configuration
API_BASE = 'https://ai-gateway.trickle-lab.tech/api/v1'
DEFAULT_MODEL = 'google/gemini-3.1-flash-image-preview'

# 30+ Design Styles: Poster Artists + Book Cover + Album Cover + Social Media
ARTIST_STYLES = {
    "auto": "let AI choose best style",
    # === Poster Artists (20) ===
    "saul-bass": "Saul Bass minimalist geometric abstraction, 2-3 colors, visual metaphor",
    "olly-moss": "Olly Moss ultra-minimal negative space, clever hidden imagery, 2 colors",
    "tyler-stout": "Tyler Stout maximalist character collage, intricate line work, organized chaos",
    "martin-ansin": "Martin Ansin Art Deco elegance, refined vintage palette, sophisticated",
    "toulouse-lautrec": "Toulouse-Lautrec flat color blocks, Japanese influence, bold silhouettes",
    "alphonse-mucha": "Alphonse Mucha Art Nouveau flowing curves, ornate floral, decorative borders",
    "jules-cheret": "Jules Chéret Belle Époque bright joyful colors, dynamic feminine figures",
    "cassandre": "Cassandre modernist geometry, Cubist planes, dramatic perspective, Art Deco",
    "milton-glaser": "Milton Glaser psychedelic pop art, innovative typography, vibrant colors",
    "drew-struzan": "Drew Struzan painted realism, epic cinematic, warm nostalgic glow",
    "kilian-eng": "Kilian Eng geometric futurism, precise technical lines, cool sci-fi palette",
    "laurent-durieux": "Laurent Durieux visual puns, hidden imagery, mysterious atmospheric",
    "jay-ryan": "Jay Ryan folksy handmade, single focal image, warm textured simple",
    "dan-mccarthy": "Dan McCarthy ultra-flat geometric abstraction, 2-3 solid colors, no gradients",
    "jock": "Jock gritty expressive brushwork, dynamic action, high contrast, raw energy",
    "shepard-fairey": "Shepard Fairey propaganda style, red black cream, halftone, political",
    "steinlen": "Steinlen social realist, expressive lines, cat motifs, high contrast",
    "josef-muller-brockmann": "Josef Müller-Brockmann Swiss grid, Helvetica, mathematical precision",
    "paul-rand": "Paul Rand playful geometry, clever visual puns, witty intelligent",
    "paula-scher": "Paula Scher typographic maximalism, layered text, vibrant expressive letters",
    # === Book Cover Designers (6) ===
    "chip-kidd": "Chip Kidd conceptual book cover, single symbolic object, bold typography, photographic metaphor, witty visual pun, Random House literary aesthetic",
    "peter-mendelsund": "Peter Mendelsund abstract literary cover, deconstructed typography, minimal symbolic elements, intellectual negative space, Knopf literary elegance",
    "coralie-bickford-smith": "Coralie Bickford-Smith Penguin Clothbound Classics, repeating decorative patterns, Art Nouveau foil stamping, jewel-tone palette, ornamental borders, fabric texture",
    "david-pearson": "David Pearson Penguin Great Ideas, bold typographic-only cover, text as visual element, minimal color, intellectual and clean, type-driven design",
    "wang-zhi-hong": "Wang Zhi-Hong East Asian book design, restrained elegant typography, confident negative space, subtle texture, balanced asymmetry, literary sophistication",
    "jan-tschichold": "Jan Tschichold modernist Penguin typography, Swiss precision grid, clean serif fonts, understated elegance, timeless typographic hierarchy",
    # === Album Cover Designers (3) ===
    "reid-miles": "Reid Miles Blue Note Records, bold asymmetric typography, high contrast black and single accent color, jazz photography silhouette, dramatic negative space, vintage vinyl",
    "david-stone-martin": "David Stone Martin Verve Records, single gestural ink brushstroke, minimalist line drawing on cream, fluid calligraphic lines, maximum negative space, improvisational energy",
    "peter-saville": "Peter Saville Factory Records extreme minimalism, single abstract form in vast empty space, monochromatic, no text on cover, conceptual and mysterious, intellectual restraint",
    # === Social Media / Chinese Aesthetic Styles (4) ===
    "wenyi": "文艺风 literary artistic style, soft muted tones, generous white space, delicate serif typography, watercolor texture, poetic atmosphere, refined and contemplative, editorial book review aesthetic",
    "guochao": "国潮风 Chinese contemporary trend, traditional Chinese motifs reimagined modern, bold red and gold palette, ink wash meets graphic design, cultural symbols with street art energy, 新中式",
    "rixi": "日系 Japanese aesthetic, warm film grain, soft natural light, pastel muted palette, clean minimal layout, hand-drawn accents, cozy atmosphere, wabi-sabi imperfection, zakka lifestyle",
    "hanxi": "韩系 Korean aesthetic, clean bright pastel, soft gradient backgrounds, modern sans-serif typography, dreamy ethereal quality, sophisticated minimal, Instagram-worthy composition",
    # === Generic Styles ===
    "minimal": "minimalist, centered single focal point, 2-3 color palette, clean simple",
    "atmospheric": "single strong focal element with atmospheric background, 3-4 colors",
    "negative-space": "figure-ground inversion, negative space reveals hidden element, 2 colors"
}

def get_api_key():
    """Get API key from environment variable"""
    api_key = os.getenv('AI_GATEWAY_API_KEY')
    if not api_key:
        print("Error: AI_GATEWAY_API_KEY environment variable is required.")
        print("Please set it with your AI Gateway API key.")
        sys.exit(1)
    return api_key

def ai_enhance_prompt(original_subject, design_type, user_preferences=""):
    """
    Use AI to enhance and optimize the prompt while respecting user's original intent

    Args:
        original_subject: User's original subject/idea
        design_type: Type of design (movie/book/album/event)
        user_preferences: Optional user specifications (colors, style, elements)

    Returns:
        Enhanced prompt string
    """
    api_key = get_api_key()

    enhancement_request = f"""Enhance this Mondo poster prompt while STRICTLY respecting the user's original intent:

Original Subject: {original_subject}
Design Type: {design_type}
User Preferences: {user_preferences if user_preferences else "None specified - AI can suggest"}

Create an optimized Mondo-style prompt that:
1. KEEPS the core idea from user's original subject
2. Adds ONE perfect symbolic visual element (not multiple)
3. Suggests 2-3 complementary colors (user can override)
4. Uses negative space or visual puns when possible
5. Maintains Mondo screen print aesthetic
6. Stays clean and minimal (not cluttered)

Return ONLY the enhanced prompt text, no explanations."""

    try:
        response = requests.post(
            f'{API_BASE}/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            json={
                'model': 'google/gemini-3.1-flash',
                'messages': [{'role': 'user', 'content': enhancement_request}],
                'max_tokens': 300
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        if 'choices' in result and len(result['choices']) > 0:
            enhanced = result['choices'][0]['message']['content'].strip()
            return enhanced
        else:
            print("⚠ AI enhancement failed, using standard template")
            return None

    except Exception as e:
        print(f"⚠ AI enhancement error: {e}, using standard template")
        return None

def get_format_description(aspect_ratio):
    """Get format description text matching the aspect ratio"""
    ratio_descriptions = {
        "9:16": "vertical 9:16 portrait format",
        "16:9": "horizontal 16:9 landscape format, wide cinematic composition",
        "21:9": "ultra-wide 21:9 panoramic banner format, horizontal landscape",
        "3:4": "vertical 3:4 portrait format",
        "4:3": "horizontal 4:3 landscape format",
        "1:1": "square 1:1 format",
    }
    return ratio_descriptions.get(aspect_ratio, f"{aspect_ratio} format")

def generate_prompt(subject, design_type, style="auto", ai_enhance=False, color_hint="", aspect_ratio="9:16"):
    """
    Generate Mondo-style prompt with optional AI enhancement

    Args:
        subject: The subject matter
        design_type: Type of design ("movie", "book", "album", "event")
        style: Visual style (artist name or preset)
        ai_enhance: Whether to use AI enhancement
        color_hint: Optional color preferences from user
        aspect_ratio: Aspect ratio for the image

    Returns:
        Generated prompt string
    """
    format_desc = get_format_description(aspect_ratio)

    # AI Enhancement path (respects user intent)
    if ai_enhance:
        user_prefs = f"Style: {style}, Colors: {color_hint}" if color_hint else f"Style: {style}"
        enhanced = ai_enhance_prompt(subject, design_type, user_prefs)
        if enhanced:
            return enhanced + f", Mondo poster style, screen print aesthetic, {format_desc}"

    # Standard template path
    base_elements = "Mondo poster style, screen print aesthetic, limited edition poster art"

    # Get style modifier
    style_desc = ARTIST_STYLES.get(style, ARTIST_STYLES['minimal'])

    # Build prompt based on type
    if design_type == "movie":
        prompt = f"{subject} in {base_elements}, {style_desc}, {format_desc}, clean focused composition, vintage poster aesthetic"
    elif design_type == "book":
        prompt = f"{subject} book cover in {base_elements}, {style_desc}, {format_desc}, clean typography, literary design"
    elif design_type == "album":
        prompt = f"{subject} album cover in {base_elements}, {style_desc}, square 1:1 format, vintage vinyl aesthetic"
    elif design_type == "event":
        prompt = f"{subject} event poster in {base_elements}, {style_desc}, {format_desc}, bold memorable design"
    else:
        prompt = f"{subject} in {base_elements}, {style_desc}, vintage print aesthetic"

    # Add color hint if provided
    if color_hint:
        prompt += f", color palette: {color_hint}"

    return prompt

def generate_image(prompt, output_path=None, model=DEFAULT_MODEL, aspect_ratio="9:16", input_image=None):
    """
    Generate image using AI Gateway API with optional image-to-image

    Args:
        prompt: The text prompt
        output_path: Path to save the image
        model: Model to use
        aspect_ratio: Aspect ratio
        input_image: Optional input image path for image-to-image

    Returns:
        Path to saved image or None if failed
    """
    api_key = get_api_key()

    payload = {
        'model': model,
        'prompt': prompt,
        'response_format': 'b64_json',
        'aspectRatio': aspect_ratio
    }

    # Add image-to-image support
    if input_image and os.path.exists(input_image):
        try:
            with open(input_image, 'rb') as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
                payload['image'] = img_b64
                payload['mode'] = 'image-to-image'
                print(f"📷 Using input image: {input_image}")
        except Exception as e:
            print(f"⚠ Could not load input image: {e}")

    print(f"🎨 Generating with {model}")
    print(f"📐 Aspect ratio: {aspect_ratio}")
    print(f"✍️  Prompt: {prompt[:80]}..." if len(prompt) > 80 else f"✍️  Prompt: {prompt}")
    print("⏳ Please wait...\n")

    try:
        response = requests.post(
            f'{API_BASE}/images/generations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'Origin': 'https://trickle.so'
            },
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        if 'data' in result and len(result['data']) > 0:
            b64_data = result['data'][0].get('b64_json')
            if b64_data:
                image_data = base64.b64decode(b64_data)

                if not output_path:
                    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    output_path = f"outputs/mondo-{timestamp}.png"

                os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(image_data)

                print(f"✅ Saved to {output_path}")
                return output_path
            else:
                print("❌ No image data in response")
                return None
        else:
            print("❌ Invalid response format")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def generate_comparison(subject, design_type, styles, aspect_ratio="9:16", colors=""):
    """
    Generate 3-column comparison of different styles

    Args:
        subject: Subject matter
        design_type: Type of design
        styles: List of 3 style names
        aspect_ratio: Aspect ratio
        colors: Optional color hint

    Returns:
        Path to comparison image
    """
    print(f"\n{'='*80}")
    print(f"🎨 GENERATING 3-STYLE COMPARISON")
    print(f"{'='*80}\n")

    images = []
    labels = []

    for i, style in enumerate(styles, 1):
        print(f"\n[{i}/3] Generating {style} style...")
        prompt = generate_prompt(subject, design_type, style, color_hint=colors, aspect_ratio=aspect_ratio)

        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        temp_path = f"outputs/temp-{style}-{timestamp}.png"

        result = generate_image(prompt, temp_path, aspect_ratio=aspect_ratio)
        if result:
            images.append(result)
            labels.append(style)
        else:
            print(f"⚠ Failed to generate {style}, skipping")

    if len(images) < 2:
        print("❌ Not enough images generated for comparison")
        return None

    # Create side-by-side comparison
    try:
        pil_images = [Image.open(img) for img in images]

        # Resize to same height
        target_height = min(img.height for img in pil_images)
        pil_images = [img.resize((int(img.width * target_height / img.height), target_height))
                     for img in pil_images]

        # Create comparison canvas
        total_width = sum(img.width for img in pil_images) + (len(pil_images) - 1) * 20  # 20px spacing
        comparison = Image.new('RGB', (total_width, target_height + 50), 'white')
        draw = ImageDraw.Draw(comparison)

        # Paste images side by side
        x_offset = 0
        for i, (img, label) in enumerate(zip(pil_images, labels)):
            comparison.paste(img, (x_offset, 0))

            # Add label
            label_text = label.upper().replace('-', ' ')
            bbox = draw.textbbox((0, 0), label_text)
            text_width = bbox[2] - bbox[0]
            text_x = x_offset + (img.width - text_width) // 2
            draw.text((text_x, target_height + 15), label_text, fill='black')

            x_offset += img.width + 20

        # Save comparison
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        comparison_path = f"outputs/comparison-{timestamp}.png"
        comparison.save(comparison_path)

        # Clean up temp files
        for img_path in images:
            try:
                os.remove(img_path)
            except:
                pass

        print(f"\n✅ Comparison saved to {comparison_path}")
        return comparison_path

    except Exception as e:
        print(f"❌ Error creating comparison: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Mondo Style Design Generator with AI optimization, comparison mode, and 20 artist styles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎨 20 Artist Styles Available:
  Classic: saul-bass, toulouse-lautrec, alphonse-mucha, jules-cheret, cassandre
  Modern: olly-moss, tyler-stout, martin-ansin, drew-struzan, milton-glaser
  Contemporary: kilian-eng, dan-mccarthy, jock, shepard-fairey, jay-ryan

Examples:
  # AI-enhanced prompt (respects your original idea)
  python3 generate_mondo_enhanced.py "Blade Runner" movie --ai-enhance

  # 3-style comparison
  python3 generate_mondo_enhanced.py "Dune" movie --compare saul-bass,olly-moss,kilian-eng

  # Image-to-image transformation
  python3 generate_mondo_enhanced.py "noir thriller" movie --input poster.jpg --style saul-bass

  # With color preferences
  python3 generate_mondo_enhanced.py "Jazz Festival" event --style jules-cheret --colors "vibrant yellow, deep blue, red"

  # Specific artist style
  python3 generate_mondo_enhanced.py "Akira" movie --style kilian-eng
        """
    )

    parser.add_argument('subject', help='Subject matter (e.g., "Blade Runner", "1984 novel")')
    parser.add_argument('type', choices=['movie', 'book', 'album', 'event'],
                       help='Type of design to create')
    parser.add_argument('--style', choices=list(ARTIST_STYLES.keys()), default='auto',
                       help='Artist style (default: auto)')
    parser.add_argument('--ai-enhance', action='store_true',
                       help='Use AI to optimize prompt (respects your original intent)')
    parser.add_argument('--compare', type=str,
                       help='Generate 3-style comparison (comma-separated, e.g., "saul-bass,olly-moss,jock")')
    parser.add_argument('--input', type=str,
                       help='Input image for image-to-image transformation')
    parser.add_argument('--colors', type=str, default='',
                       help='Color preferences (e.g., "orange, teal, black")')
    parser.add_argument('--aspect-ratio', '--ratio', dest='aspect_ratio', default='9:16',
                       help='Aspect ratio (default: 9:16)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Model to use')
    parser.add_argument('--no-generate', action='store_true',
                       help='Only show prompt without generating')
    parser.add_argument('--list-styles', action='store_true',
                       help='List all available artist styles')

    args = parser.parse_args()

    # List styles
    if args.list_styles:
        print("\n🎨 20 Greatest Poster Artists - Available Styles:\n")
        for style, desc in ARTIST_STYLES.items():
            print(f"  {style:25} → {desc}")
        print()
        return

    # Comparison mode
    if args.compare:
        styles = [s.strip() for s in args.compare.split(',')]
        if len(styles) != 3:
            print("❌ Comparison requires exactly 3 styles (e.g., --compare saul-bass,olly-moss,jock)")
            sys.exit(1)

        generate_comparison(args.subject, args.type, styles, args.aspect_ratio, args.colors)
        return

    # Single generation mode
    prompt = generate_prompt(args.subject, args.type, args.style, args.ai_enhance, args.colors, args.aspect_ratio)

    print(f"\n{'='*80}")
    print("🎨 MONDO POSTER PROMPT")
    print(f"{'='*80}")
    print(f"{prompt}")
    print(f"{'='*80}\n")

    if not args.no_generate:
        output_path = generate_image(prompt, args.output, args.model, args.aspect_ratio, args.input)
        if not output_path:
            sys.exit(1)
    else:
        print("✓ Prompt generated. Use without --no-generate to create image.")

if __name__ == '__main__':
    main()
