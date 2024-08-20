import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { $el, ComfyDialog } from "../../scripts/ui.js";
const style = `
.comfy-modal-close {
    width: calc(100% - 64px);
    bottom: 10px;
    position: absolute;
    overflow: hidden;
    left: 32px;
}
#cm-manager-dialog {
	width: 1000px;
	height: 520px;
	box-sizing: content-box;
	z-index: 10000;
	overflow-y: auto;
}
.cm-file-list{
    width: 100%;
    box-sizing: border-box;
    height: 320px;
    overflow-y: auto;
    padding: 10px;
    margin: 0;
    transition: all 0.3s;
}
.cm-file-list li{
    list-style: none;
    display: flex;
    justify-content: space-between;
    width: 100%;
    height: 30px;
    line-height: 30px;
    color: #FFF;
    border-bottom: 1px solid #ccc;
}
@keyframes spinner {
    to {
        transform: rotate(360deg);
    }
}
.spinner {
    border: 4px solid rgba(0, 0, 0, 0.2);
    border-top-color: #3498db;
    border-radius: 50%;
    width: 14px;
    height: 14px;
    animation: spinner 1.5s linear infinite;
}
.spinner-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 14px;
    margin-top: 8px;
}
.bubble {
    position: relative;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background-color: #4CAF50;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-size: 14px;
    margin-top: 8px;
}
.bubble::before {
    content: '✔';
    position: absolute;
    font-size: 14px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
`
class myDialog extends ComfyDialog {
    constructor() {
        super();
        this.filesAry = []
        this.uploadId = ''
        const close_button = $el("button.comfy-modal-close", { type: "button", textContent: "Close", onclick: () => this.close() });
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("div.cm-title", {}, [
                        $el("font", { size: 6, color: "white" }, [`BizyAir Workflow`]),]
                    ),
                    $el("br", {}, []),
                    $el("input.cm-input-file-modle", { type: "file", webkitdirectory: true, mozdirectory: true, odirectory: true, msdirectory: true, onchange: (e) => this.onFileChange(e) }),
                    $el("br", {}, []),
                    $el('ul.cm-file-list', {}, []),
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
        this.uploadId = this.generateUUID()
        this.filesAry = [...e.srcElement.files]
        console.log(document.querySelector('.cm-file-list'))
        this.filesAry.forEach(file => {
            document.querySelector('.cm-file-list').appendChild(
                $el('li', {}, [
                    $el("span", {}, [`${ file.webkitRelativePath }`]),
                    // $el("span", {}, [`${ file.size }`]),
                    // $el("span", {}, [`${ file.type }`]),
                    $el("span.spinner-container", {}, [
                        $el("span.spinner", {}, [])
                    ]),
                ])
            )
        })
        this.todoUpload()
    }
    todoUpload() {
        if (this.filesAry.length === 0) {
            return;
        }
        const file = this.filesAry.shift();
        this.fetchApiToUpload(file, (data) => {
            // 处理上传结果
            if (data.code === 20000) {
                // 如果上传成功，继续上传下个文件
                const cmFileList = document.querySelectorAll('.cm-file-list li');
                const i = cmFileList.length - this.filesAry.length - 1;
                cmFileList[i].querySelector('.spinner-container').innerHTML = `<span class="bubble"></span>`;
                document.querySelector('.cm-file-list').scrollTop = cmFileList[i].offsetTop - 134;
                this.todoUpload();
            } else {
                // 如果上传失败，显示错误信息
                app.ui.dialog.show(`${data.message}`);
            }
        });
    }
    fetchApiToUpload(file, fn) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('filename', file.webkitRelativePath);
        formData.append("upload_id", this.uploadId);
        fetch('/bizyair/modelhost/file_upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Request successful', data);
            
            if (fn) {
                fn(data)
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
