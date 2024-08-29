def remove_dup(items: list[dict], key: str):
    keys = set()
    output = []
    for item in items:
        v = item[key]
        if v in keys:
            continue
        keys.add(v)
        output.append(item)
    return output


def parse_lambda(lambda_str: str, value: any, default_str: str):
    try:
        parse_function = eval(lambda_str)
        if callable(parse_function):
            parsed_value = parse_function(value)
            return parsed_value
        else:
            print(f"Invalid parse function: {lambda_str}")
            return default_str
    except Exception as e:
        print(f"Failed to parse with error: {e}")
        return default_str
