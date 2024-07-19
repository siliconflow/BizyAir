def to_camel_case(snake_str):
    if not snake_str.startswith("BizyAir_"):
        raise ValueError("String must start with 'BizyAir_' prefix")
    snake_str = snake_str.replace("BizyAir_", "BizyAir ")
    return snake_str


def register_node(display_name=None):
    def decorator(cls):
        class_name = cls.__name__
        camel_case_name = to_camel_case(class_name)
        display_name_to_use = display_name if display_name else f"☁️{camel_case_name}"
        NODE_CLASS_MAPPINGS[class_name] = cls
        NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name_to_use

        assert cls.CATEGORY.startswith("☁️BizyAir")
        return cls

    return decorator


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
