import re
import openai
import langdetect
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def format_multiline_quote(text):
    if text is None:
        return "번역 실패 또는 결과 없음."
    lines = text.split('\n')
    return '\n'.join([f"> *{line}*" if line.strip() else "> " for line in lines])

def split_text_by_sentence(text, max_length):
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
    sentences = sentence_endings.split(text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def translate_message(content, logger):
    try:
        url_pattern = re.compile(r'(https?://\S+)|(www\.\S+)')
        masked_content = re.sub(url_pattern, "[link]", content)
        if masked_content.strip() == "[link]" * len(re.findall(url_pattern, content)):
            return "이 메시지는 링크만 포함하고 있어 번역하지 않습니다."
        try:
            source_language = langdetect.detect(masked_content)
            if source_language not in ['ko', 'en']:
                source_language = 'en'
            # logger.debug(f"감지된 언어: {source_language}")
        except langdetect.LangDetectException:
            logger.warning("언어 감지 실패, 기본값(영어) 사용")
            source_language = "en"
        target_language = "en" if re.search(r'[a-zA-Z]', masked_content) else "ko"
        if source_language == "en":
            target_language = "ko"
        elif source_language != "en" and target_language == "ko":
            target_language = "en"
        paragraphs = masked_content.split('\n\n')
        translated_paragraphs = []
        for paragraph in paragraphs:
            chunks = split_text_by_sentence(paragraph, max_length=500)
            translated_chunks = []
            for chunk in chunks:
                prompt = f"Translate this {source_language} text to {target_language}: {chunk}"
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content":
                        "You are a translation assistant. Translate the content into the specified target language.For Korean translations, use '-요' endings for general conversation. Avoid formal endings like '-다 / -습니다'. Use informal endings or slang for personal thoughts, casual statements, or emotions. Keep the translation concise and clear, avoiding filler language. Preserve bullet points, numbered lists, and formatting. and do not avoid slang."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.07
                )
                translated_chunks.append(response['choices'][0]['message']['content'])
            translated_paragraphs.append(' '.join(translated_chunks))
        translated_text = '\n\n'.join(translated_paragraphs)
        translated_text = translated_text.replace('자산', '작업물')
        logger.info(f'감지 언어 {source_language} ==> 번역 언어 {target_language}')
        return translated_text
    except Exception as e:
        logger.error(f'번역 중 오류 발생: {e}')
        return None