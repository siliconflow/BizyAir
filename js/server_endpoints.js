let app, api;

try {
    const module1 = await import("../../scripts/app.js");
    app = module1.app;
    const module2 = await import("../../scripts/api.js");
    api = module2.api;
} catch (e) {
  try {
    const module1 = await import("/scripts/app.js");
    app = module1.app;
    const module2 = await import("/scripts/api.js");
    api = module2.api;
  } catch (e) {
    throw e;
  }
}
import { toast } from './subassembly/toast.js';

app.registerExtension({
	name: "bizyair.server.endpoint.switch.dlg",
    async setup() {
        function messageHandler(event) {
            toast({
                content: event.detail.message,
                type: 'succeed',
                center: true
            })
        }
        api.addEventListener("bizyair.server.endpoint.switch", messageHandler);
    },
})
