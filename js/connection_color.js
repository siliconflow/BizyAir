let app;

try {
    const module1 = await import("../../scripts/app.js");
    app = module1.app;
} catch (e) {
  try {
    const module1 = await import("/scripts/app.js");
    app = module1.app;
  } catch (e) {
    throw e;
  }
}

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
