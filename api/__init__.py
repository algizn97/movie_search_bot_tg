def truncate_description(description: str, max_length: int = 950) -> str:
    """
    Обрезает строку описания до заданной длины, сохраняя текст до последней точки.

    Эта функция принимает строку описания и максимальную длину. Если длина описания
    превышает максимальную, функция обрезает его до последней точки, чтобы сохранить
    целостность предложений. Если точка не найдена, описание будет обрезано до
    максимальной длины.

    :param description: Описание, которое необходимо обрезать (строка).
    :param max_length: Максимальная длина обрезанного описания (по умолчанию 950).

    :return: Обрезанное описание (строка), которое не превышает max_length символов.
              Если длина исходного описания меньше или равна max_length,
              возвращается оригинальная строка.
    """

    if len(description) <= max_length:
        return description

    last_period_index = description.rfind(".")

    if last_period_index != -1 and last_period_index <= max_length:
        return description[: last_period_index + 1]

    for i in range(max_length - 1, -1, -1):
        if description[i] == ".":
            return description[: i + 1]

    return description[:max_length]
