import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "bizyair.custom.connectionColorByType",
    async setup() {
        Object.assign(app.canvas.default_connection_color_byType, {
            BIZYAIR_MODEL: '#7C5AEC',
            BIZYAIR_CLIP: '#FFF4C4',
            BIZYAIR_VAE: '#FF5959',
            BIZYAIR_CONDITIONING: '#967117',
        })
    },
});
