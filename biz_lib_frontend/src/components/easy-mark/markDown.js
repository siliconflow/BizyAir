import EasyMDE from '@/components/easy-mark/easyMarked.js'
import { uploadImage } from '@/api/public'
import  {useToaster}  from '@/components/modules/toats/index'

export default class MarkDown {
    constructor(options) {
        if (!options || !options.containerId) {
            throw new Error('containerId is required');
        }
        
        this.options = options;
        this.isPreview = options.isPreview;
        this.containerId = options.containerId;
        this.content = options.content;
        this.isUploading = false;
        this.easyMDE = null;
        this.onUploadStatusChange = options.onUploadStatusChange;
    
        
        this.createContainer();
        this.loadStyle();
        this.init();
    }

    createContainer() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            throw new Error(`can't find container element with id ${this.containerId}`);
        }

        const existingEditor = container.querySelector(`#${this.containerId}-editor`);
        if (existingEditor) {
            throw new Error(`Editor already exists in container with id ${this.containerId}`);
        }

        container.style.position = 'relative';
        container.style.width = '100%';
        container.style.height = '100%';

        const wrapper = document.createElement('div');
        wrapper.style.position = 'absolute';
        wrapper.style.width = '100%';
        wrapper.style.height = '100%';
        wrapper.style.transition = 'all 0.2s';
        
        const textarea = document.createElement('textarea');
        textarea.id = `${this.containerId}-editor`;
        if(this.content) {
            textarea.value = this.content;
        }
        
        wrapper.appendChild(textarea);
        container.appendChild(wrapper);
        
        this.wrapper = wrapper;
        this.textarea = textarea;
        this.originalDomId = textarea.id;
    }

    loadStyle(){
        const existingLink = document.querySelector('link[href*="easymarked.mini.css"]');
        if (existingLink) return;
        
        try {
            const cssPath = new URL('./easymarked.mini.css', import.meta.url).href;
            const linkElement = document.createElement('link');
            linkElement.rel = 'stylesheet';
            linkElement.href = cssPath;
            document.head.appendChild(linkElement);
        } catch (error) {
            console.error('load style error:', error);
        }
    }

    init() {
        if (this.isPreview) {
            this.preview(this.content);
        } else {
            this.editor();
        }
    }

    getCommonConfig() {
        return {
            element: this.textarea,
            spellChecker: false,
            height: "100%",
            tabSize: 4,
            status: false
        };
    }

    setFullscreen(isFullscreen) {
        console.log('isFullscreen', isFullscreen)
        const body = document.querySelector('body');
        if(isFullscreen) {
            body.style.pointerEvents = 'auto';
            body.appendChild(this.wrapper);
            this.wrapper.style.position = 'fixed';
            this.wrapper.style.left = '0';
            this.wrapper.style.top = '0';
            this.wrapper.style.width = '100vw';
            this.wrapper.style.height = '100vh';
            this.wrapper.style.zIndex = '99999';
            this.wrapper.style.background = '#222';
           
            setTimeout(() => {
                const dialogElement = document.querySelector('[role="dialog"][tabindex="-1"]')
                if (dialogElement) {
                  dialogElement.removeAttribute('tabindex')
                }
            }, 0)

        } else {
            const container = document.getElementById(this.containerId);
            body.style.pointerEvents = 'none';
            container.appendChild(this.wrapper);
            this.wrapper.style.position = 'absolute';
            this.wrapper.style.left = '';
            this.wrapper.style.top = '';
            this.wrapper.style.width = '100%';
            this.wrapper.style.height = '100%';
            this.wrapper.style.zIndex = '';
            this.wrapper.style.background = '';

            setTimeout(() => {
            const dialogElement = document.querySelector('[role="dialog"]')
            if (dialogElement) {
              dialogElement.setAttribute('tabindex', '-1')
                }
            }, 0)
        }
    }

    editor() {
        const config = {
            ...this.getCommonConfig(),
            autoDownloadFontAwesome: false,
            autofocus: true,
            theme: 'dark',
            autosave: {
                enabled: true,
                uniqueId: 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
                    const r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
                    return r.toString(16);
                }),
                delay: 1000,
            },
            uploadImage: true,
            toolbar: [
              "heading-smaller",
              "bold",
              "italic",
              "link",
              "code", 
               {
                    name: "upload-image",
                    action: function customFunction(editor) {
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.accept = 'image/*';
                        input.multiple = true;
                        input.onchange =async () => {
                            const files = Array.from(input.files || []);
                            if (files.length > 3) {
                                useToaster.warning('Maximum 3 files can be uploaded at once');
                                return;
                            }
                            useToaster(`uploading images ${files.length}, please wait`);
                            const uploadPromises = files.map((file) => {
                                return new Promise((resolve) => {
                                    config.imageUploadFunction(
                                        file,
                                        (url) => {
                                            resolve({
                                                success: true,
                                                fileName: file.name,
                                                url: url
                                            });
                                        },
                                        (error) => {
                                            resolve({
                                                success: false,
                                                fileName: file.name,
                                                error: error
                                            });
                                        }
                                    );
                                });
                            });
    
                            const results = await Promise.all(uploadPromises);
                            const successfulUploads = results.filter(r => r.success);
                            
                            if (successfulUploads.length > 0) {
                                const markdownContent = successfulUploads
                                    .map(result => `![${result.fileName}](${result.url})`)
                                    .join('\n');
                                editor.codemirror.replaceSelection(markdownContent + '\n');
                            }
                        };
                        input.click();
                    },
                    className: "fa fa-upload",
                    title: "upload image",
              },
              "unordered-list",
              "ordered-list",
              "|",
              "preview",
              "side-by-side",
              "fullscreen",
              {
                    name: "others",
                    className: "fa fa-ellipsis-v",
                    title: "others buttons",
                    children: [
                        "table",
                        {
                            name: "image",
                            action: EasyMDE.drawImage,
                            className: "fa fa-picture-o",
                            title: "Image",
                        },
                        {
                            name: "quote",
                            action: EasyMDE.toggleBlockquote,
                            className: "fa fa-percent",
                            title: "Quote",
                        },
                        
                    ]
                },
            ],
            onToggleFullScreen: (isFullscreen) => {
                this.setFullscreen(isFullscreen);
            },
            imageUploadFunction:async (file, onSuccess, onError) => {
                try {
                    if (!file.type.startsWith('image/')) {
                        useToaster.warning('please upload image file')
                        return;
                    }
                    const maxSize = 20 * 1024 * 1024;
                    if (file.size > maxSize) {
                        useToaster.warning('image size cannot exceed 20MB')
                        return;
                    }
                    let retryCount = 3;
                    this.options.onUploadStatusChange?.(true);
                    while (retryCount > 0) {
                        try {
                            const res = await uploadImage(file);
                            if (res?.data?.url) {
                                useToaster.success(`${file.name} uploaded successfully`);
                                onSuccess(res.data.url);
                                break;
                            } 
                        } catch (err) {
                            retryCount--;
                            if (retryCount === 0) {
                                useToaster.error(`${file.name} upload failed`);
                                onError(err);
                            } else {
                                await new Promise(resolve => setTimeout(resolve, 1000));
                                continue;
                            }
                        } finally {
                            this.options.onUploadStatusChange?.(false);
                        }
                    }
                } catch (error) {
                    useToaster.error(`Image ${index} upload failed`);
                    onError('upload image file error');
                    this.options.onUploadStatusChange?.(false);
                }
            },
          
            events: {
                "fullscreenChange": (_instance, isFullscreen) => {
                    this.setFullscreen(isFullscreen);
                },
                "paste": async (instance, e) => {
                    if (e.clipboardData && e.clipboardData.items) {
                        const imageItems = Array.from(e.clipboardData.items)
                            .filter(item => item.type.indexOf("image") !== -1);
                        
                        if (imageItems.length > 3) {
                            useToaster.warning('Maximum 3 files can be uploaded at once');
                            return;
                        }
                        useToaster(`uploading images ${imageItems.length}, please wait`);
                        const uploadPromises = imageItems.map((item) => {
                            const file = item.getAsFile();
                          
                            return new Promise((resolve) => {
                                config.imageUploadFunction(
                                    file,
                                    (url) => {
                                        resolve({
                                            success: true,
                                            fileName: file.name,
                                            url: url
                                        });
                                    },
                                    (error) => {
                                        resolve({
                                            success: false,
                                            fileName: file.name,
                                            error: error
                                        });
                                    },
                                );
                            });
                        });
            
                        const results = await Promise.all(uploadPromises);
                        const successfulUploads = results.filter(r => r.success);
                        
                        if (successfulUploads.length > 0) {
                            const markdownContent = successfulUploads
                                .map(result => `![${result.fileName}](${result.url})`)
                                .join('\n');
                            instance.codemirror.replaceSelection(markdownContent + '\n');
                        }
                    }
                }
            }
        };
        
        this.easyMDE = new EasyMDE(config);
    }

    preview(content) {
        const config = {
            ...this.getCommonConfig(),
            autofocus: false,
            autosave: false,
            toolbar: false,
            sideBySideFullscreen: false,
            forceSync: true,
            status: false,
            initialValue: content,
        };
        
        this.easyMDE = new EasyMDE(config);
        this.easyMDE.togglePreview();
    }



    getValue() {
        return this.easyMDE ? this.easyMDE.value() : '';
    }
}