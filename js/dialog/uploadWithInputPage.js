import { $el } from "../../../scripts/ui.js";
import { check_model_exists, model_types, check_folder, submit_upload } from "../apis.js"
import { dialog } from '../subassembly/dialog.js';
import { subscribe, unsubscribe } from '../subassembly/subscribers.js'

export const uploadWithInputPage = async () => {
    const Q = (selector) => document.querySelector(selector);
    const QAll = (selector) => document.querySelectorAll(selector);
    const resType = await model_types();
    const typeList = resType.data;
    const elOptions = typeList.map(item => $el("option", { value: item.value }, [item.label]))
    const temp = {
        filesAry: [],
        content: $el("div.comfy-modal-content.comfy-modal-content-file", [
            $el("div.bizyair-form-item", {}, [
                $el("span.bizyair-form-label", {}, ['Type']),
                $el("select.cm-input-item", {
                    onchange: function () {
                        this.className = this.className.replace(/cm-input-item-error/g, '')
                    }
                }, [
                    ...elOptions
                ]),
                $el("i.bizyair-form-qa", {
                    onmouseover: function () {
                        temp.showQA(this, 'Model types.')
                    },
                    onmouseout: function () {
                        temp.hideQA(this)
                    }
                }, ['?']),
            ]),
            $el("div.bizyair-form-item", {}, [
                $el("span.bizyair-form-label", {}, ['Name']),
                $el("input.cm-input-item", {
                    type: "text",
                    placeholder: "The remote folder name",
                    id: 'bizyair-model-name',
                    onchange: function () {
                        this.className = this.className.replace(/cm-input-item-error/g, '')
                    }
                }),
                $el("i.bizyair-form-qa", {
                    onmouseover: function () {
                        temp.showQA(this, 'Remote folder name of the model')
                    },
                    onmouseout: function () {
                        temp.hideQA(this)
                    }
                }, ['?']),
            ]),
            $el("div.bizyair-form-item", {}, [
                $el("span.bizyair-form-label", {}, ['Local Path']),
                $el("input.cm-input-item", {
                    type: "text",
                    placeholder: "Please enter the local file path.",
                    id: 'bizyair-input-file-box',
                    onchange: function (e) {
                        this.className = this.className.replace(/cm-input-item-error/g, '');
                        temp.onFileMultiChange(e)
                    }
                }),
                $el("i.bizyair-form-qa", {
                    onmouseover: function () {
                        temp.showQA(this, 'Please specify the ABSOLUTE PATH of the directory to be uploaded.')
                    },
                    onmouseout: function () {
                        temp.hideQA(this)
                    }
                }, ['?']),
            ]),
            $el("br", {}, []),
            $el('ul.bizyair-file-list', {}, []),
            $el("p.tips-in-upload", {
                id: 'tips-in-upload',
                style: { display: 'none' }
            }, ["Please do not close this dialog box or perform any other operations while the file is uploading."]),
        ]
        ),
        showQA(ele, text) {
            $el('span.bizyair-form-qa-hint', {
                parent: ele,
            }, [text])
        },
        hideQA(ele) {
            ele.querySelector('.bizyair-form-qa-hint').remove()
        },
        queryExists() {
            const type = Q('select.cm-input-item').value
            const name = Q('input.cm-input-item').value
            check_model_exists(type, name).then(data => {
                if (data.code === 20000) {
                    if (data.data.exists) {
                        this.confirmExists()
                    } else {
                        QAll('.spinner-container').forEach(e => {
                            e.innerHTML = `<span class="spinner"></span>`
                        })
                        this.todoUpload()
                    }
                }

            });
        },
        confirmExists() {
            dialog({
                title: "The model already exists",
                content: "Do you want to overwrite it?",
                yesText: "Yes",
                noText: "No",
                onYes: () => {
                    QAll('.spinner-container').forEach(e => {
                        e.innerHTML = `<span class="spinner"></span>`
                    })
                    this.todoUpload();
                    return true
                },
                onNo: () => {
                    this.unDisabledInput()
                    QAll('.spinner-container').forEach(e => {
                        e.innerHTML = ''
                    })
                }
            })
        },
        toSubmit() {
            const elSelect = Q('select.cm-input-item')
            const elInput = Q('input.cm-input-item')
            const cmFileList = Q('.bizyair-file-list')
            const bizyairInputFileBox = Q('#bizyair-input-file-box')

            if (!elSelect.value) {
                dialog({
                    tyoe: 'warning',
                    content: "Please select model type",
                    noText: 'Close'
                })
                elSelect.className = `${elSelect.className} cm-input-item-error`
                return

            }
            if (!elInput.value) {
                dialog({
                    type: 'warning',
                    content: "Please input model name",
                    noText: 'Close'
                })
                elInput.className = `${elInput.className} cm-input-item-error`
                return
            }
            if (/^[A-Za-z0-9\u4e00-\u9fa5]([A-Za-z0-9\u4e00-\u9fa5-_]*)$/.test(elInput.value) == false) {
                dialog({
                    type: 'warning',
                    content: "Please enter English letters, Chinese characters, numbers, or - or _.",
                    noText: 'Close'
                })
                elInput.className = `${elInput.className} cm-input-item-error`
                return
            }
            if (cmFileList.querySelectorAll('li').length == 0) {
                dialog({
                    type: 'warning',
                    content: "Please select files",
                    noText: 'Close'
                })
                bizyairInputFileBox.className = `${bizyairInputFileBox.className} cm-input-item-error`
                return
            }
            this.queryExists()

        },
        disabledInput() {
            Q('input.cm-input-item').disabled = true
            Q('select.cm-input-item').disabled = true
            Q('#bizyair-input-file-box').disabled = true

            Q('#bizyair-upload-submit').style.display = 'none'
            Q('#bizyair-upload-reset').style.display = 'none'
        },
        unDisabledInput() {
            Q('input.cm-input-item').disabled = false
            Q('select.cm-input-item').disabled = false
            Q('#bizyair-input-file-box').disabled = false

            Q('#bizyair-upload-reset').style.display = 'block'
        },
        todoUpload() {
            const elSelect = Q('select.cm-input-item')
            const elInput = Q('input.cm-input-item')

            submit_upload({
                upload_id: this.uploadId,
                name: elInput.value,
                type: elSelect.value,
                overwrite: true
            });
            Q('#tips-in-upload').style.display = 'block'
            this.disabledInput()
        },
        onFileMultiChange(e) {
            Q('.bizyair-file-list').innerHTML = ''
            check_folder(e.target.value).then(data => {
                this.filesAry = data.data.files
                this.uploadId = data.data.upload_id
                data.data.files.forEach(file => {
                    Q('.bizyair-file-list').appendChild(
                        $el('li', {}, [
                            $el("span", {}, [`${file.path}`]),
                            $el("span.spinner-container", {}, []),
                        ])
                    )
                })
            })
        },
        redraw() {
            Q('#bizyair-model-name').value = ''
            Q('.bizyair-file-list').innerHTML = ''
            Q('#bizyair-input-file-box').value = ''
        }
    }
    const fnMessage = (data) => {
        const res = JSON.parse(data.data);
        if (res.type == "progress") {
            const cmFileList = QAll('.bizyair-file-list li');
            const index = temp.filesAry.map(e => e.path).indexOf(res.data.path)
            if (index !== -1) {
                cmFileList[index].querySelector('.spinner-container').innerHTML = `${res.data.progress}`;
                Q('.bizyair-file-list').scrollTop = cmFileList[index].offsetTop - 134;
            }
        }
        if (res.type == "status") {
            if (res.data.status == "finish") {
                Q('#bizyair-upload-submit').style.display = 'none'
                temp.unDisabledInput()
                Q('#tips-in-upload').style.display = 'none'
                dialog({
                    type: 'succeed',
                    content: "The model has been uploaded successfully.",
                    noText: 'Close'
                });

            }
        }
    };
    subscribe('socketMessage', fnMessage);

    dialog({
        content: temp.content,
        yesText: 'Submit',
        yesId: 'bizyair-upload-submit',
        neutralId: 'bizyair-upload-reset',
        noText: 'Close',
        neutralText: 'Reset',
        onYes: () => {
            temp.toSubmit()
        },
        onNeutral: () => {
            Q('#bizyair-upload-submit').style.display = 'block';
            temp.redraw()
        },
        onNo: () => {
            unsubscribe('socketMessage', fnMessage)
            temp.redraw()
        }
    })
}
