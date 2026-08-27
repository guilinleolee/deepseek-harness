# Remix X/Twitter Posts

## Goal

Summarize each builder's recent tweets into a 2-4 sentence insight that captures their key idea, prediction, or hot take. Write for practitioners who want signal, not noise.

## Rules

### Format
- Lead with the builder's **full name and role/company** (e.g. "Box CEO Aaron Levie" or just "Gabor Cselovszki"). Never use @ handles.
- Bold predictions and hot takes at the start of the summary.
- 2-4 sentences total.
- Every tweet **MUST include its URL** from the JSON. No URL = do not include.
- Skip: mundane tweets, self-promotion, replies to others unless they contain original opinions.

### What to Include
- Original opinions, bold predictions, strong claims
- Announcements about products, features, or research
- Technical insights about AI/ML/engineering
- Market observations with reasoning
- Controversial takes the builder is known for

### What to Skip
- "Great thread" endorsements of others
- Generic praise or validation
- Event announcements without substance
- Purely personal life updates

### Output

```
[Full Name, Role/Company](tweet_url) on what they said and why it matters.
[2-4 sentence summary]
```

## Examples

**Good:**
Anthropic CEO Dario Amodei on why frontier AI development is accelerating faster than most people realize, and what that means for safety timelines. He argues that the gap between current capabilities and AGI is closing faster than internal projections suggested 18 months ago, which changes how we should think about alignment timelines.

**Skip:**
@somebuilder "Excited to announce our new feature! 🚀" — self-promotion, no substance.

**Good:**
Gabor Cselovszki on why long-context reasoning with small models (1B-3B parameters) is an underrated research direction. He shows that models with 128K+ context can outperform larger models on certain tasks when given explicit chain-of-thought prompts, challenging the assumption that bigger is always better for reasoning tasks.

**Skip:**
@somebuilder "Thanks everyone for the supportive replies! 🙏" — generic gratitude.
