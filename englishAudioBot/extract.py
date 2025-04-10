SENTENCE_PATTERN = "Предложения для запоминания:"
PHRASES_PATTERN = "Фразы для запоминания:"
WORDS_PATTERN = "Слова для запоминания:"


def extract_data(message: str):
    blocks = {
        "sentences": [],
        "phrases": [],
        "words": [],
    }

    # Найдём индексы начала каждого блока
    patterns = {
        "sentences": SENTENCE_PATTERN,
        "phrases": PHRASES_PATTERN,
        "words": WORDS_PATTERN
    }

    # Соберём позиции начала блоков
    positions = []
    for key, pattern in patterns.items():
        idx = message.find(pattern)
        if idx != -1:
            positions.append((idx, key, pattern))

    # Отсортируем по позиции в тексте
    positions.sort()

    for i, (start_idx, key, pattern) in enumerate(positions):
        # Найдём конец текущего блока — это начало следующего блока или конец текста
        end_idx = positions[i + 1][0] if i + 1 < len(positions) else len(message)

        # Извлекаем блок текста между pattern и end_idx
        block_text = message[start_idx + len(pattern):end_idx].strip()

        # Разбиваем на строки, очищаем от "- "
        lines = [line.strip().removeprefix("- ").strip() for line in block_text.splitlines() if line.strip()]
        blocks[key] = lines

    return blocks


# Пример использования
if __name__ == "__main__":
    test_msg = """1. Could you spare me a moment? — Не уделите мне минуточку?

2. May I ask you a question? — Можно спросить Вас?

3. Sorry for interrupting you — Извините, что вмешиваюсь.

4. Are you busy at the moment? — Вы сейчас заняты?

Предложения для запоминания:
- Are you busy at the moment?
- Sorry for interrupting you
- May I ask you a question?
- Could you spare me a moment?

Фразы для запоминания:
- spare me a moment"""

    result = extract_data(test_msg)
    print(result)
