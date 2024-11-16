import { api } from "../../../scripts/api.js";
import { app } from "../../scripts/app.js";
import { dialog } from './subassembly/dialog.js';

app.registerExtension({
	name: "bizyair.server.endpoint.switch.dlg",
    async setup() {
        function messageHandler(event) {
            dialog({
                content: event.detail.message,
                type: 'succeed',
                noText: 'Close'
            })
        }
        api.addEventListener("bizyair.server.endpoint.switch", messageHandler);
    },
})
