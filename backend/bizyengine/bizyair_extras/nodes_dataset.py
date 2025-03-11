from bizyengine.core import BizyAirBaseNode


class TrainDatasetAdd(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "dataset_config": ("JSON",),
                "width": (
                    "INT",
                    {"min": 64, "default": 1024, "tooltip": "base resolution width"},
                ),
                "height": (
                    "INT",
                    {"min": 64, "default": 1024, "tooltip": "base resolution height"},
                ),
                "batch_size": (
                    "INT",
                    {
                        "min": 1,
                        "default": 2,
                        "tooltip": "Higher batch size uses more memory and generalizes the training more",
                    },
                ),
                "dataset_path": (
                    [
                        "to choose",
                    ],
                    # "STRING",
                    # {
                    #     "multiline": True,
                    #     "default": "",
                    #     "tooltip": "path to dataset, root is the 'ComfyUI' folder, with windows portable 'ComfyUI_windows_portable'",
                    # },
                ),
                "dataset_version_id": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
                "class_tokens": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "trigger_word",
                        "tooltip": "aka trigger word, if specified, will be added to the start of each caption, if no captions exist, will be used on it's own",
                    },
                ),
                "enable_bucket": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "enable buckets for multi aspect ratio training",
                    },
                ),
                "bucket_no_upscale": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "don't allow upscaling when bucketing",
                    },
                ),
                "num_repeats": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "tooltip": "number of times to repeat dataset for an epoch",
                    },
                ),
                "min_bucket_reso": (
                    "INT",
                    {
                        "default": 256,
                        "min": 64,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "min bucket resolution",
                    },
                ),
                "max_bucket_reso": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 64,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "max bucket resolution",
                    },
                ),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("dataset",)
    # FUNCTION = "create_config"
    CATEGORY = "FluxTrainer"
