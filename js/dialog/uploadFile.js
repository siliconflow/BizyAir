import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";
// import { style } from "../subassembly/style.js";
import { ConfirmDialog } from "../subassembly/confirm.js";

export function uploadPage (typeList) {
    const close_button = $el("button.comfy-bizyair-close", { 
        type: "button", 
        textContent: "Close", 
        onclick: () => this.close() 
    });
    const submit_button = $el("button.comfy-bizyair-submit", { 
        type: "button", 
        textContent: "submit", 
        onclick: () => this.toSubmit() 
    });
    const elOptions = typeList.map(item => $el("option", { value: item.value }, [item.label]))
    const temp = {
        content: $el("div.comfy-modal-content.comfy-modal-content-file",[
                $el("select.cm-input-item", {
                    onchange: function() {
                        this.className = this.className.replace(/cm-input-item-error/g, '')
                    }
                }, [
                    ...elOptions
                ]),
                $el("input.cm-input-item", { type: "text", placeholder: "model name", onchange: function() {
                    this.className = this.className.replace(/cm-input-item-error/g, '')
                } }),
                $el('div.cm-input-file-box', {}, [
                    $el("p.cm-word-file-modle", {}, ['select folder']),
                    $el("inputbizyair-input-file-modle", { 
                        type: "file", 
                        webkitdirectory: true, 
                        mozdirectory: true, 
                        odirectory: true, 
                        msdirectory: true, 
                        onchange: (e) => temp.onFileChange(e) 
                    }),
                ]),
                $el("br", {}, []),
                $el('ul.bizyair-file-list', {}, []),
                $el('div.cm-bottom-footer', {}, [close_button, submit_button]),
            ]
        ),
        queryExists() {
            const type = document.querySelector('select.cm-input-item').value
            const name = document.querySelector('input.cm-input-item').value
            fetch(`/bizyair/modelhost/check_model_exists`, {
                method: 'POST',
                body: JSON.stringify({ type, name })
            }).then(response => response.json()).then(data => {
                if (data.code === 20000) {
                    if (data.data.exists) {
                        this.confirmExists()
                    } else {
                        this.todoUpload()
                    }
                }
                
            });
        },
        confirmExists() {
            new ConfirmDialog({
                title: "BizyAir Workflow",
                message: "Are you sure to submit?",
                yesText: "Yes",
                noText: "No",
                onYes: () => {
                    this.todoUpload()
                },
                onNo: () => {
                    document.querySelector('.comfy-modal-submit').disabled = false
                    document.querySelector('.comfy-modal-submit').innerText = 'submit'
                }
            })
        },
        toSubmit() {
            const elSelect = document.querySelector('select.cm-input-item')
            const elInput = document.querySelector('input.cm-input-item')
            const cmFileList = document.querySelector('.bizyair-file-list')
            const cmWordFileMmodle = document.querySelector('.cm-word-file-modle')
            
            if (!elSelect.value) {
                new ConfirmDialog({
                    title: "",
                    warning: true,
                    message: "Please select model type"
                })
                elSelect.className = `${elSelect.className} cm-input-item-error`
                return
    
            }
            if (!elInput.value) {
                new ConfirmDialog({
                    title: "",
                    warning: true,
                    message: "Please input model name"
                })
                elInput.className = `${elInput.className} cm-input-item-error`
                return
            }
            if (cmFileList.querySelectorAll('li').length == 0) {
                new ConfirmDialog({
                    title: "",
                    warning: true,
                    message: "Please select files"
                })
                cmWordFileMmodle.className = `${cmWordFileMmodle.className} cm-input-item-error`
                return
            }
            document.querySelector('.comfy-modal-submit').disabled = true
            document.querySelector('.comfy-modal-submit').innerText = 'Waiting...'
            this.signs = []
            this.queryExists()
        },
        todoUpload() {
            if (this.filesAry.length === 0) {
                this.modelUpload()
                return;
            }
            const file = this.filesAry.shift();
            this.fetchApiToUpload(file, (data) => {
                // 处理上传结果
                if (data.code === 20000) {
                    // 如果上传成功，继续上传下个文件
                    const cmFileList = document.querySelectorAll('.bizyair-file-list li');
                    const i = cmFileList.length - this.filesAry.length - 1;
                    cmFileList[i].querySelector('.spinner-container').innerHTML = `<span class="bubble"></span>`;
                    document.querySelector('.bizyair-file-list').scrollTop = cmFileList[i].offsetTop - 134;
                    this.signs.push({
                        sign: data.data.sign,
                        path: file.webkitRelativePath
                    });
                    this.todoUpload();
                } else {
                    // 如果上传失败，显示错误信息
                    app.ui.dialog.show(`${data.message}`);
                }
            });
        },
        modelUpload() {
            const elSelect = document.querySelector('select.cm-input-item')
            const elInput = document.querySelector('input.cm-input-item')
            fetch('/bizyair/modelhost/model_upload', {
                method: 'POST',
                body: JSON.stringify({ 
                    upload_id: this.uploadId,
                    name: elInput.value,
                    type: elSelect.value,
                    overwrite: true,
                    files: this.signs
                 })
            }).then(response => response.json()).then(data => {
                console.log(data)
                document.querySelector('.comfy-modal-submit').style.display = 'none'
            })
        },
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
        },
        generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
                return r.toString(16);
            });
        },
        onFileChange(e) {
            const cmWordFileMmodle = document.querySelector('.cm-word-file-modle')
            cmWordFileMmodle.className = cmWordFileMmodle.className.replace(/cm-input-item-error/g, '')
            this.uploadId = this.generateUUID()
            this.filesAry = [...e.srcElement.files]
            console.log(document.querySelector('.bizyair-file-list'))
            this.filesAry.forEach(file => {
                document.querySelector('.bizyair-file-list').appendChild(
                    $el('li', {}, [
                        $el("span", {}, [`${ file.webkitRelativePath }`]),
                        $el("span.spinner-container", {}, [
                            // $el("span.spinner", {}, [])
                        ]),
                    ])
                )
            })
        }
    }
    return temp
}