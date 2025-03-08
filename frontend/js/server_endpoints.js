import { api } from "../../../scripts/api.js";
import { app } from "../../scripts/app.js";
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
