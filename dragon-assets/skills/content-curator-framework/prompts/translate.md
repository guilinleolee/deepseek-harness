# Chinese Translation Rules

When the user's language preference is set to "zh" or "bilingual", translate the entire digest into natural simplified Mandarin following these rules.

## Mandarin Style
- Write **full natural simplified Mandarin** — not machine-translate Chinese
- Sound like a thoughtful Chinese tech writer, not a literal translation
- Use natural Chinese sentence structures and flow
- Keep the professional but conversational tone from the English version

## English Words to Keep in English
These terms are industry-standard in English and should remain untranslated:
- AI, LLM, GPU, API, fine-tuning, RAG, token, prompt, agent, transformer
- Model names (Claude, GPT, Gemini, Llama, Qwen, etc.)
- Product names (OpenAI, Anthropic, Google DeepMind, etc.)
- Proper nouns in English

## Numbers and Units
- Keep numbers as Arabic numerals (1, 10, 2024)
- Translate units where natural: "10%" stays "10%"
- Use Chinese punctuation: "。" for sentences, "、" for lists

## Formatting Rules
- **NO em-dashes (—)** — use "——" or natural Chinese connectors like "而且" or "此外"
- Keep the same section headers: "## Official Blog Posts", "## X / Twitter", "## Podcasts"
- Bold the same way: **bold text** (markdown bold works the same in Chinese)
- URLs stay unchanged

## Special Terms
Keep these in English where they appear in original text:
- "Scaling" (noun/verb) — keep as "scaling"
- "Hallucination" in AI context — keep as "hallucination"
- "Context window" — keep as "context window"
- "Inference" — keep as "inference"
- "Zero-shot" / "Few-shot" — keep as "zero-shot" / "few-shot"
- "Agent" — keep as "agent" (already in the allow-list)

## Bilingual Mode
When language is "bilingual", interleave English and Chinese **paragraph by paragraph**:
- English paragraph, then Chinese translation directly below, then next English paragraph, then Chinese below, etc.
- Use each content item's URL once in English and once in Chinese
- Do NOT output all English first then all Chinese

## Tone
- Professional but conversational
- Confident, not hedging ("这意味着" not "这可能意味着")
- Direct, not overly academic
- Practical implications in plain language
