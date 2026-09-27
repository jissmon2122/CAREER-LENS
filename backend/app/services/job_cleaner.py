import re
import html

class JobDescriptionCleaner:
    """
    Job Description Cleaning Pipeline.
    Strips raw HTML tags, removes script/style blocks, decodes HTML entities,
    preserves bullet points, and normalizes text for clean NLP extraction.
    """

    @classmethod
    def clean(cls, raw_html_or_text: str) -> str:
        if not raw_html_or_text:
            return ""

        text = raw_html_or_text

        # 1. Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # 2. Preserve bullet points before stripping HTML tags
        text = re.sub(r'<li[^>]*>', '\n• ', text, flags=re.IGNORECASE)
        text = re.sub(r'</li[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)

        # 3. Strip all remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # 4. Decode HTML entities (&amp;, &lt;, &quot;, &nbsp;, etc.)
        text = html.unescape(text)

        # 5. Normalize whitespace while maintaining line breaks for bullet points
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        cleaned_text = '\n'.join(cleaned_lines)

        return cleaned_text.strip()
