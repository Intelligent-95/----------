def render_template(template, **kwargs):
    result = template
    for key, value in kwargs.items():
        placeholder = '{{ ' + key + ' }}'

        result = result.replace(placeholder, str(value))

    for key, values in kwargs.items():
        if isinstance(values, list):
            start_tag = '{% for ' + key + ' in ' + key + ' %}'
            end_tag = '{% endfor %}'
            start_index = result.find(start_tag)
            end_index = result.find(end_tag, start_index)

            while start_index != -1 and end_index != -1:
                loop_block = result[start_index + len(start_tag):end_index]

                new_block = ''
                for item in values:
                    new_block += loop_block.replace('{{ ' + key + ' }}', str(item))

                result = result[:start_index] + new_block + result[end_index + len(end_tag):]

                start_index = result.find(start_tag)
                end_index = result.find(end_tag, start_index)

    return result