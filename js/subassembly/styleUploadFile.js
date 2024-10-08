export const styleUploadFile = `
.bizyair-modal{
    width: 100vw;
    height: 100vh;
    position: fixed;
    left: 0;
    top: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: none;
    z-index: 10000000;
}
.bizyair-dialog{
	width: 1200px;
	height: 520px;
	box-sizing: content-box;
	z-index: 10000;
	overflow-y: auto;
}
.bizyair-dialog-sml{
    width: 640px;
    height: 300px;
}

.bizyair-header-tab{
    display: flex;
    border-bottom: 2px solid var(--border-color);
}
.bizyair-header-tab-item{
    width: 180px;
    height: 40px;
    line-height: 40px;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    cursor: pointer;
    color: var(--input-text);
    border: 2px solid var(--border-color);
    border-bottom: 0;
}
.bizyair-header-tab-item:last-child{
    border-left: 0;
}
.bizyair-header-tab-item-active, .bizyair-header-tab-item:hover{
    color: var(--p-content-color);
    background-color: var(--comfy-menu-bg);
}
.bizyair-header-tab-item-active{
    margin-bottom: -2px;
    height: 42px;
}
.bizyair-model-filter-item{
    width: 100%;
    display: flex;
    gap: 40px;
}
.bizyair-model-filter-lis{
    display: flex;
    flex: 1;
}
.bizyair-filter-label{
    width: 60px;
    line-height: 30px;
}
.bizyair-model-filter-item .cm-input-item{
    flex: 1;
}
.comfy-modal-content-file{
    margin-top: 40px;
}
.comfy-modal-content{
    width: 1000px;
    height: 100%;
}
.comfy-modal-content-sml{
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.cm-bottom-footer {
    width: calc(100% - 64px);
    bottom: 10px;
    position: absolute;
    overflow: hidden;
    left: 32px;
    display: flex;
}
.comfy-bizyair-close {
    flex: 1;
}
.comfy-bizyair-submit{
    flex: 1;
}
.cm-input-file-box{
    width: 100%;
    height: 30px;
    position: relative;
}
p.cm-word-file-modle{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 30px;
    line-height: 30px;
    background-color: var(--comfy-input-bg);
    border-radius: 8px;
    color: var(--input-text);
    padding: 0 10px;
    margin: 0;
    box-sizing: border-box;
    overflow: hidden;
    border: 1px solid var(--border-color);
}
.bizyair-input-file-modle {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 30px;
    opacity: 0;
    cursor: pointer;
    z-index: 100;
    opacity: 0;
}
.bizyair-file-list{
    width: 100%;
    box-sizing: border-box;
    height: 200px;
    overflow-y: auto;
    padding: 10px;
    margin: 0;
    transition: all 0.3s;
    position: relative;
    z-index: 10;
}
.bizyair-file-list li{
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
.cm-input-item{
    height: 30px;
    margin-bottom: 10px;
    padding: 0 10px;
}
select.cm-input-item{
    margin: 0 0 10px 0;
}
p.cm-input-item-error,
div.cm-input-item-error,
select.cm-input-item-error,
input.cm-input-item-error{
    border: 1px solid var(--error-text);
}
.confirm-word{
    color: var(--input-text);
}
.comfy-modal-confirm{
    width: 100%;

}
.bizyair-dialog-confirm{
    width: 300px;
	height: 160px;
	box-sizing: content-box;
	z-index: 100001;
}
.bizyair-link{
    color: var(--bizyair-link);
    margin-left: 10px;
}
.bizyair-model-list{
    width: 1000px;
    height: 360px;
    margin-top: 40px;
    color: var(--input-text);
    overflow-y: auto;
}
.bizyair-model-list-item{
    line-height: 40px;
    border-bottom: 1px solid var(--border-color);
}
.bizyair-model-list-item:last-child{
    border-bottom: 0;
}
.bizyair-model-list-item-header{
    font-weight: bold;
    font-size: 14px;
    width: 100%;
    display: flex;
    line-height: 40px;
    height: 40px;
    justify-content: space-between;
    border: 0;
    font-size: 18px;
    color: rgba(221, 221, 221, 0.6);
}
.bizyair-model-list-item-body{
    border: 1px solid var(--border-color);
    background-color: var(--comfy-input-bg);
    padding: 0 20px;
    border-radius: 8px;
}
.bizyair-model-list-item-body .bizyair-flex-item{
    padding: 0 40px
}
.bizyair-model-list-item-folder{
    width: 100%;
    height: 40px;
    font-weight: bold;
    display: flex;
    border-bottom: 1px solid var(--border-color);
}
.bizyair-icon-fold{
    width: 18px;
    height: 18px;
    line-height: 18px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    margin: 12px 8px 0 0;
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1024 1024'%3E%3Cpath fill='%23fff' d='M765.7 486.8L314.9 134.7A7.97 7.97 0 0 0 302 141v77.3c0 4.9 2.3 9.6 6.1 12.6l360 281.1l-360 281.1c-3.9 3-6.1 7.7-6.1 12.6V883c0 6.7 7.7 10.4 12.9 6.3l450.8-352.1a31.96 31.96 0 0 0 0-50.4'/%3E%3C/svg%3E");
}
.bizyair-icon-fold.unfold{
    transform: rotate(90deg);
}
.bizyair-model-list-content{
    flex: 1;
    display: flex;
    justify-content: space-between;
}
.bizyair-model-handle{
    display: flex;
}
.bizyair-icon-delete{
    width: 24px;
    height: 24px;
    cursor: pointer;
    margin: 8px 0 0 8px;
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M7.616 20q-.672 0-1.144-.472T6 18.385V6H5V5h4v-.77h6V5h4v1h-1v12.385q0 .69-.462 1.153T16.384 20zM17 6H7v12.385q0 .269.173.442t.443.173h8.769q.23 0 .423-.192t.192-.424zM9.808 17h1V8h-1zm3.384 0h1V8h-1zM7 6v13z'/%3E%3C/svg%3E");
}
.bizyair-icon-delete:hover{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f93e3e' d='M7.616 20q-.672 0-1.144-.472T6 18.385V6H5V5h4v-.77h6V5h4v1h-1v12.385q0 .69-.462 1.153T16.384 20zM17 6H7v12.385q0 .269.173.442t.443.173h8.769q.23 0 .423-.192t.192-.424zM9.808 17h1V8h-1zm3.384 0h1V8h-1zM7 6v13z'/%3E%3C/svg%3E");
}
.bizyair-icon-share{
    width: 24px;
    height: 24px;
    cursor: pointer;
    margin: 8px 0 0 8px;
    background-repeat: no-repeat;
    background-size: 20px 20px;
    background-position: center center;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ddd' d='M12 9a3 3 0 0 0-3 3a3 3 0 0 0 3 3a3 3 0 0 0 3-3a3 3 0 0 0-3-3m0 8a5 5 0 0 1-5-5a5 5 0 0 1 5-5a5 5 0 0 1 5 5a5 5 0 0 1-5 5m0-12.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5'/%3E%3C/svg%3E");
}
.bizyair-icon-share:hover{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23e44f42' d='M12 9a3 3 0 0 0-3 3a3 3 0 0 0 3 3a3 3 0 0 0 3-3a3 3 0 0 0-3-3m0 8a5 5 0 0 1-5-5a5 5 0 0 1 5-5a5 5 0 0 1 5 5a5 5 0 0 1-5 5m0-12.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5'/%3E%3C/svg%3E");
}
.bizyair-icon-unshared{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ddd' d='M11.83 9L15 12.16V12a3 3 0 0 0-3-3zm-4.3.8l1.55 1.55c-.05.21-.08.42-.08.65a3 3 0 0 0 3 3c.22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53a5 5 0 0 1-5-5c0-.79.2-1.53.53-2.2M2 4.27l2.28 2.28l.45.45C3.08 8.3 1.78 10 1 12c1.73 4.39 6 7.5 11 7.5c1.55 0 3.03-.3 4.38-.84l.43.42L19.73 22L21 20.73L3.27 3M12 7a5 5 0 0 1 5 5c0 .64-.13 1.26-.36 1.82l2.93 2.93c1.5-1.25 2.7-2.89 3.43-4.75c-1.73-4.39-6-7.5-11-7.5c-1.4 0-2.74.25-4 .7l2.17 2.15C10.74 7.13 11.35 7 12 7'/%3E%3C/svg%3E");
}
.bizyair-icon-unshared:hover{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23e44f42' d='M11.83 9L15 12.16V12a3 3 0 0 0-3-3zm-4.3.8l1.55 1.55c-.05.21-.08.42-.08.65a3 3 0 0 0 3 3c.22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53a5 5 0 0 1-5-5c0-.79.2-1.53.53-2.2M2 4.27l2.28 2.28l.45.45C3.08 8.3 1.78 10 1 12c1.73 4.39 6 7.5 11 7.5c1.55 0 3.03-.3 4.38-.84l.43.42L19.73 22L21 20.73L3.27 3M12 7a5 5 0 0 1 5 5c0 .64-.13 1.26-.36 1.82l2.93 2.93c1.5-1.25 2.7-2.89 3.43-4.75c-1.73-4.39-6-7.5-11-7.5c-1.4 0-2.74.25-4 .7l2.17 2.15C10.74 7.13 11.35 7 12 7'/%3E%3C/svg%3E");
}
.bizyair-model-list-item-child{
    display: flex;
    justify-content: space-between;
    width: 100%;
    height: 40px;
    border-bottom: 1px solid var(--border-color);
}
.bizyair-flex-item{
    flex: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    padding: 0 60px;
}
.bizyair-flex-item-avaulable{
    width: 100px;
    text-align: center;
}
.bizyair-flex-item-avaulable .spinner-container{
    margin-top: 14px;
}
.bizyair-form-item{
    display: flex;
    margin-bottom: 10px;
    width: 100%;
    position: relative;
}
.spinner-container-in-list{
    width: 14px;
    margin-left: 34px;
}
.available-word{
    margin-left: 18px;
}
.bizyair-form-label{
    width: 100px;
    line-height: 30px;
    font-size: 16px;
    color: var(--input-text);
}
.bizyair-form-item .cm-input-item, .bizyair-form-item .cm-input-file-box{
    flex: 1;
}
.bizyair-form-item-subset{
    display: flex;
    flex: 1;
}
.bizyair-form-qa{
    width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    font-size: 16px;
    color: var(--input-text);
    margin-left: 10px;
    cursor: pointer;
    font-style: normal;
    background-color: var(--comfy-input-bg);
    border-radius: 50%;
    margin-top: 5px;
    display: block;
}

.upload-size-hint{
    position: absolute;
    left: 104px;
    bottom: -30px;
    margin: 0;
    padding: 0;
    color: #e6a23c;
    height: 30px;
    line-height: 30px;
}
p.tips-in-upload{
    margin: 4px 0 0 0;
    color: #e6a23c;
}
.radio-container{
    margin-right: 20px;
    line-height: 32px;
    cursor: pointer;
}
`
