def render_template(template, **kwargs):
    result = template
    for key, value in kwargs.items():
        placeholder = '{{ ' + key + ' }}'

        # Заменяем место-для-подстановки в шаблоне на значение
        result = result.replace(placeholder, str(value))

    # Добавим поддержку цикла for
    for key, values in kwargs.items():
        if isinstance(values, list):
            # Ищем блок {% for key in values %} ... {% endfor %}
            start_tag = '{% for ' + key + ' in ' + key + ' %}'
            end_tag = '{% endfor %}'
            start_index = result.find(start_tag)
            end_index = result.find(end_tag, start_index)

            while start_index != -1 and end_index != -1:
                # Извлекаем блок между тегами
                loop_block = result[start_index + len(start_tag):end_index]

                # Генерируем новый блок с учетом цикла for
                new_block = ''
                for item in values:
                    new_block += loop_block.replace('{{ ' + key + ' }}', str(item))

                # Заменяем старый блок на новый
                result = result[:start_index] + new_block + result[end_index + len(end_tag):]

                # Поиск следующего цикла
                start_index = result.find(start_tag)
                end_index = result.find(end_tag, start_index)

    return result