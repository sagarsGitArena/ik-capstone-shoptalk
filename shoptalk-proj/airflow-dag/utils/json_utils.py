def flatten_json(nested_json, parent_key='', sep='_'):
    items = {}
    for key, value in nested_json.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            # Recursively flatten dictionaries
            items.update(flatten_json(value, new_key, sep=sep))
        elif isinstance(value, list):
            # Handle lists by iterating through elements
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    items.update(flatten_json(item, f"{new_key}_{i}", sep=sep))
                elif isinstance(item, str):
                    # Remove '\n' from strings in the list
                    items[f"{new_key}_{i}"] = item.replace('\n', '')
                else:
                    items[f"{new_key}_{i}"] = item
        elif isinstance(value, str):
            # Remove '\n' from strings
            items[new_key] = value.replace('\n', '')
        else:
            # Handle other data types without modification
            items[new_key] = value
    return items