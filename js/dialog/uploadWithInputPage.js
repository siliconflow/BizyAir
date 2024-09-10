import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { ConfirmDialog } from "../subassembly/confirm.js";
import { check_model_exists, model_upload, file_upload, model_types, check_folder, submit_upload } from "../apis.js"
import { dialog } from '../subassembly/dialog.js';
import { subscribe } from '../subassembly/subscribers.js'

export const uploadWithInputPage = async () => {
    const resType = await model_types();
    const typeList = resType.data;
    const elOptions = typeList.map(item => $el("option", { value: item.value }, [item.label]))
    const temp = {
        filesAry: [],
        content: $el("div.comfy-modal-content.comfy-modal-content-file",[
                $el("div.bizyair-form-item", {}, [
                    $el("span.bizyair-form-label", {}, ['Type']),
                    $el("select.cm-input-item", {
                        onchange: function() {
                            this.className = this.className.replace(/cm-input-item-error/g, '')
                        }
                    }, [
                        ...elOptions
                    ]),
                    $el("i.bizyair-form-qa", {
                        onmouseover: function() {
                            temp.showQA(this, 'Model types.')
                        },
                        onmouseout: function() {
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
                        onchange: function() {
                            this.className = this.className.replace(/cm-input-item-error/g, '')
                        }
                    }),
                    $el("i.bizyair-form-qa", {
                        onmouseover: function() {
                            temp.showQA(this, 'Remote folder name of the model')
                        },
                        onmouseout: function() {
                            temp.hideQA(this)
                        }
                    }, ['?']),
                ]),
                $el("div.bizyair-form-item", {}, [
                    $el("span.bizyair-form-label", {}, ['Purpose']),
                    $el("input.cm-input-item", {
                        type: "text",
                        placeholder: "Please enter the local file path.",
                        id: 'bizyair-input-file-box',
                        onchange: function(e) {
                            this.className = this.className.replace(/cm-input-item-error/g, '');
                            temp.onFileMultiChange(e)
                        }
                    }),
                    $el("i.bizyair-form-qa", {
                        onmouseover: function() {
                            temp.showQA(this, 'All the files in the selected folder will be uploaded to the remote folder.')
                        },
                        onmouseout: function() {
                            temp.hideQA(this)
                        }
                    }, ['?']),
                    $el('p.upload-size-hint', { }, ['You can specify the file upload limit as needed (in MB), for example: python main.py --max-upload-size 1024']),
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
            const type = document.querySelector('select.cm-input-item').value
            const name = document.querySelector('input.cm-input-item').value
            check_model_exists(type, name).then(data => {
                if (data.code === 20000) {
                    if (data.data.exists) {
                        this.confirmExists()
                    } else {
                        document.querySelectorAll('.spinner-container').forEach(e => {
                            e.innerHTML = `<span class="spinner"></span>`
                        })
                        this.todoUpload()
                    }
                }

            });
        },
        confirmExists() {
            new ConfirmDialog({
                title: "The model already exists",
                message: "Do you want to overwrite it?",
                yesText: "Yes",
                noText: "No",
                onYes: () => {
                    document.querySelectorAll('.spinner-container').forEach(e => {
                        e.innerHTML = `<span class="spinner"></span>`
                    })
                    this.todoUpload()
                },
                onNo: () => {
                    this.unDisabledSubmit()
                    document.querySelectorAll('.spinner-container').forEach(e => {
                        e.innerHTML = ''
                    })
                }
            })
        },
        toSubmit() {
            const elSelect = document.querySelector('select.cm-input-item')
            const elInput = document.querySelector('input.cm-input-item')
            const cmFileList = document.querySelector('.bizyair-file-list')
            const bizyairInputFileBox = document.querySelector('#bizyair-input-file-box')

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
                bizyairInputFileBox.className = `${bizyairInputFileBox.className} cm-input-item-error`
                return
            }
            this.disabledSubmit()
            // this.signs = []
            this.queryExists()

        },
        disabledInput() {
            document.querySelector('input.cm-input-item').disabled = true
            document.querySelector('select.cm-input-item').disabled = true
            document.querySelector('#bizyair-input-file-box').disabled = true
        },
        unDisabledInput() {
            document.querySelector('input.cm-input-item').disabled = false
            document.querySelector('select.cm-input-item').disabled = false
            document.querySelector('#bizyair-input-file-box').disabled = false

            document.querySelector('#bizyair-upload-submit').disabled = false
            document.querySelector('#bizyair-upload-submit').innerText = 'Submit'
        },
        todoUpload() {
            
            const elSelect = document.querySelector('select.cm-input-item')
            const elInput = document.querySelector('input.cm-input-item')

            submit_upload({
                upload_id: this.uploadId,
                name: elInput.value,
                type: elSelect.value,
                overwrite: true
            });
            document.querySelector('#tips-in-upload').style.display = 'block'
            
            this.disabledInput()

            if (document.querySelector('#tips-in-upload')) return
            document.querySelector('#tips-in-upload').style.display = 'block'
            if (this.filesAry.length === 0) {
                this.modelUpload()
                return;
            }
            const file = this.filesAry.shift();
            this.fetchApiToUpload(file, (data) => {
                if (data.code === 20000) {
                    const cmFileList = document.querySelectorAll('.bizyair-file-list li');
                    const i = cmFileList.length - this.filesAry.length - 1;
                    cmFileList[i].querySelector('.spinner-container').innerHTML = `<span class="bubble"></span>`;
                    document.querySelector('.bizyair-file-list').scrollTop = cmFileList[i].offsetTop - 134;
                    this.signs.push({
                        sign: data.data.sign,
                        path: file.webkitRelativePath || file.name
                    });
                    this.todoUpload();
                } else {
                    app.ui.dialog.show(`${data.message}`);
                }
            });
        },
        modelUpload() {
            const elSelect = document.querySelector('select.cm-input-item')
            const elInput = document.querySelector('input.cm-input-item')
            model_upload({
                upload_id: this.uploadId,
                name: elInput.value,
                type: elSelect.value,
                overwrite: true,
                files: this.signs
            }).then(data => {
                document.querySelector('#bizyair-upload-submit').style.display = 'none'
                this.unDisabledInput()
                document.querySelector('#tips-in-upload').style.display = 'none'
                new ConfirmDialog({
                    message: "The model has been uploaded successfully."
                })
            })
        },
        fetchApiToUpload(file, fn) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('filename', file.webkitRelativePath);
            formData.append("upload_id", this.uploadId);
            file_upload(formData).then(data => {
                console.log('Request successful', data);

                if (fn) {
                    fn(data)
                }
            })
            .catch(error => {
                this.unDisabledInput()
                console.log(this.unDisabledInput)
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
            const file = e.target.files[0];
            this.filesAry.push(file)
            const bizyairInputFileBox = document.querySelector('#bizyair-input-file-box')
            bizyairInputFileBox.className = bizyairInputFileBox.className.replace(/cm-input-item-error/g, '')
            if (!this.uploadId) {
                this.uploadId = this.generateUUID()
            }
            document.querySelector('.bizyair-file-list').appendChild(
                $el('li', {}, [
                    $el("span", {}, [`${ file.name }`]),
                    $el("span.spinner-container", {}, []),
                ])
            )
        },
        onFileMultiChange(e) {
            console.log(e.target.value)
            
            if (!this.uploadId) {
                this.uploadId = this.generateUUID()
            }
            document.querySelector('.bizyair-file-list').innerHTML = ''
            check_folder(e.target.value).then(data => {
                this.filesAry = data.data.files
                this.uploadId = data.data.upload_id
                data.data.files.forEach(file => {
                    document.querySelector('.bizyair-file-list').appendChild(
                        $el('li', {}, [
                            $el("span", {}, [`${ file.path }`]),
                            // $el("span", {}, [`${ file.size }`]),
                            $el("span.spinner-container", {}, []),
                        ])
                    )
                })
            })
        },
        disabledSubmit() {
            document.querySelector('#bizyair-upload-submit').disabled = true
            document.querySelector('#bizyair-upload-submit').innerText = 'Waiting...'
        },
        unDisabledSubmit() {
            document.querySelector('#bizyair-upload-submit').disabled = false
            document.querySelector('#bizyair-upload-submit').innerText = 'Submit'
        },
        redraw() {
            document.querySelector('#bizyair-model-name').value = ''
            document.querySelector('.bizyair-file-list').innerHTML = ''
            document.querySelector('#bizyair-input-file-box').value = ''
        }
    }
    subscribe('socketMessage', (data) => {
        const res = JSON.parse(data.data);
        console.log(res)
        if (res.type == "progress") {
            console.log(res.data)
            const cmFileList = document.querySelectorAll('.bizyair-file-list li');
            const index = temp.filesAry.map(e => e.path).indexOf(res.data.path)
            if (index != -1) {
                cmFileList[index].querySelector('.spinner-container').innerHTML = `${res.data.progress}`;
                document.querySelector('.bizyair-file-list').scrollTop = cmFileList[index].offsetTop - 134;
            }

            // const i = cmFileList.length - temp.filesAry.length - 1;
            // cmFileList[i].querySelector('.spinner-container').innerHTML = `<span class="bubble"></span>`;
            // document.querySelector('.bizyair-file-list').scrollTop = cmFileList[i].offsetTop - 134;
        }
        if (res.type == "status") {
            console.log(res.data)
            if (res.data.status == "finish") {
                document.querySelector('#bizyair-upload-submit').style.display = 'none'
                temp.unDisabledInput()
                document.querySelector('#tips-in-upload').style.display = 'none'
                new ConfirmDialog({
                    message: "The model has been uploaded successfully."
                });
            }
        }
    });

    dialog({
        content: temp.content,
        yesText: 'Submit',
        yesId: 'bizyair-upload-submit',
        noText: 'Close',
        onYes: () => {
            temp.toSubmit()
            // return true
        },
    })
}
