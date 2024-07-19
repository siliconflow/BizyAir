import nodes

LOGO = "☁️"
PREFIX = f"{LOGO}BizyAir"


def to_camel_case(snake_str):
    if not snake_str.startswith("BizyAir_"):
        raise ValueError("String must start with 'BizyAir_' prefix")
    snake_str = snake_str.replace("BizyAir_", "BizyAir ")
    return snake_str


def validate_category(cls):
    if not hasattr(cls, "CATEGORY"):
        raise ValueError(f"{cls.__name__} must have a CATEGORY attribute")
    if not cls.CATEGORY.startswith(PREFIX):
        raise ValueError(f"CATEGORY in {cls.__name__} must start with {PREFIX}")


def register_node(custom_display_name=None):
    def decorator(cls):
        validate_category(cls)

        class_name = cls.__name__
        prefix = "BizyAir"
        cls_name = to_camel_case(class_name)
        base_name = cls_name[len(prefix) :]
        if base_name in nodes.NODE_DISPLAY_NAME_MAPPINGS:
            display_name = f"☁️{prefix} {nodes.NODE_DISPLAY_NAME_MAPPINGS[base_name]}"
        else:
            display_name = f"☁️{prefix} {base_name}"

        final_display_name = (
            custom_display_name if custom_display_name else display_name
        )
        NODE_CLASS_MAPPINGS[class_name] = cls
        NODE_DISPLAY_NAME_MAPPINGS[class_name] = final_display_name

        assert cls.CATEGORY.startswith(f"☁️{prefix}")
        return cls

    return decorator


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
