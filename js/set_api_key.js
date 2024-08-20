import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { $el, ComfyDialog } from "../../scripts/ui.js";
const style = `
.comfy-modal-close {
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 40px;

}
`
class myDialog extends ComfyDialog {
    constructor() {
        super();
        this.filesAry = []
        const close_button = $el("button.comfy-modal-close", { type: "button", textContent: "Close", onclick: () => this.close() });
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("tr.cm-title", {}, [
                        $el("font", { size: 6, color: "white" }, [`BizyAir Workflow`]),]
                    ),
                    $el("br", {}, []),
                    $el("input.cm-input-file-modle", { type: "file", webkitdirectory: true, mozdirectory: true, odirectory: true, msdirectory: true, onchange: (e) => this.onFileChange(e) }),
                    $el("br", {}, []),
                    close_button,
                ]
            );

        content.style.width = '100%';
        content.style.height = '100%';

        this.element = $el("div.comfy-modal", { id: 'cm-manager-dialog', parent: document.body }, [content]);
        this.element.style.display = "block";
    }
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
            return r.toString(16);
        });
    }
    onFileChange(e) {
        console.log(e.srcElement.files)
        this.filesAry = [...e.srcElement.files].map(e => ({ file: e, id: this.generateUUID() }))
        console.log(this.filesAry)
        this.todoUpload()
    }
    todoUpload() {
        if (this.filesAry.length === 0) {
            return
        }
        const fileIndex = this.filesAry.length - 1;
        const { file, id } = this.filesAry.pop()
        console.log(fileIndex)
        this.fetchApiToUpload(file, id, () => {
            this.todoUpload()
        })
    }
    fetchApiToUpload(file, id, fn) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('filename', file.webkitRelativePath);
        formData.append("upload_id", id);
        formData.append('id', id);
        fetch('/bizyair/modelhost/file_upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Request successful', data);
            
            if (fn) {
                fn()
            }
        })
        .catch(error => {
            console.error('Error during AJAX request', error);
        });
    }
}
app.registerExtension({
    name: "BizyAir_SetAPIKey",

    async setup() {
        const menu = document.querySelector(".comfy-menu");
        // app.ui.dialog.show(`Installing... 'asd'`);
        $el("style", {
            textContent: style,
            parent: document.head,
        });
        new myDialog()
        // 添加分隔线
        const separator = document.createElement("div");
        separator.style.margin = "20px 0";
        separator.style.width = "100%";
        separator.style.height = "2px";
        separator.style.backgroundColor = "gray";
        menu.append(separator);

        // 创建按钮
        const BizyAir_SetAPIKey = document.createElement("button");
        BizyAir_SetAPIKey.textContent = "BizyAir Key";
        BizyAir_SetAPIKey.style.backgroundColor = "rgb(130, 88, 245)"; // 设置按钮背景颜色
        BizyAir_SetAPIKey.style.border = "none";
        BizyAir_SetAPIKey.style.color = "white";
        BizyAir_SetAPIKey.style.padding = "10px 20px";
        BizyAir_SetAPIKey.style.textAlign = "center";
        BizyAir_SetAPIKey.style.textDecoration = "none";
        BizyAir_SetAPIKey.style.display = "inline-block";
        BizyAir_SetAPIKey.style.fontSize = "16px";
        BizyAir_SetAPIKey.style.margin = "4px 2px";
        BizyAir_SetAPIKey.style.cursor = "pointer";
        BizyAir_SetAPIKey.style.borderRadius = "12px";

        const apiKeyUrl = `${location.href.replace(/\/$/, '')}/bizyair/set-api-key`;
        BizyAir_SetAPIKey.onclick = () => {
            window.open(apiKeyUrl, "Set API Key");
        };

        menu.append(BizyAir_SetAPIKey);

        const response = await api.fetchApi("/bizyair/get_api_key",
            { method: "GET" });
        if (response.status === 200) {
            console.log("get SiliconCloud api key successfuly")
        } else {
            alert(`Please click "BizyAir Key" button to set API key first,
you can get your key from cloud.siliconflow.cn,
or you can only use nodes locally.`);
            const text = await response.text();
            console.log("not set api key:", text)
        }
    }
});
