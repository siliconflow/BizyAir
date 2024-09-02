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
	width: 1000px;
	height: 520px;
	box-sizing: content-box;
	z-index: 10000;
	overflow-y: auto;
}
.bizyair-dialog-sml{
    width: 600px;
    height: 240px;
}

.bizyair-header-tab{
    display: flex;
    border-bottom: 2px solid var(--border-color);
}
.bizyair-header-tab-item{
    width: 160px;
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
    width: 100%;
    height: 100%;
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
    height: 250px;
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
    width: 100%;
    height: 360px;
    margin-top: 40px;
    color: var(--input-text);
    overflow-y: auto;
}
.bizyair-model-list-item-header{
    font-weight: bold;
    font-size: 18px;
    width: 100%;
    display: flex;
    line-height: 40px;
    height: 40px;
    justify-content: space-between;
}
.bizyair-model-list-item{
    line-height: 40px;
    border-bottom: 1px solid var(--border-color);
}
.bizyair-model-list-item:hover .bizyair-icon-delete{
    display: block;
}
.bizyair-model-list-item-folder{
    width: 100%;
    height: 40px;
    font-weight: bold;
    display: flex;
    border-bottom: 1px solid var(--border-color);
}
.bizyair-icon-unfold{
    width: 24px;
    height: 24px;
    line-height: 24px;
    text-align: center;
    cursor: pointer;
    font-size: 18px;
    color: var(--input-text);
    margin: 8px 8px 0 0;
    background-color: var(--comfy-input-bg);
    border: 1px solid var(--border-color);
    border-redius: 4px;
}
.bizyair-icon-delete{
    width: 24px;
    height: 24px;
    cursor: pointer;
    margin: 8px 0 0 8px;
    display: none;
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M7.616 20q-.672 0-1.144-.472T6 18.385V6H5V5h4v-.77h6V5h4v1h-1v12.385q0 .69-.462 1.153T16.384 20zM17 6H7v12.385q0 .269.173.442t.443.173h8.769q.23 0 .423-.192t.192-.424zM9.808 17h1V8h-1zm3.384 0h1V8h-1zM7 6v13z'/%3E%3C/svg%3E");
}
.bizyair-icon-delete:hover{
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f93e3e' d='M7.616 20q-.672 0-1.144-.472T6 18.385V6H5V5h4v-.77h6V5h4v1h-1v12.385q0 .69-.462 1.153T16.384 20zM17 6H7v12.385q0 .269.173.442t.443.173h8.769q.23 0 .423-.192t.192-.424zM9.808 17h1V8h-1zm3.384 0h1V8h-1zM7 6v13z'/%3E%3C/svg%3E");
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
    padding-right: 60px;
}
.bizyair-flex-item-avaulable{
    width: 100px;
}
.bizyair-form-item{
    display: flex;
    margin-bottom: 10px;
    width: 100%;
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
    position: relative;
}
.bizyair-form-qa-hint{
    position: absolute;
    background-color: var(--comfy-input-bg);
    border: 1px solid var(--border-color);
    padding: 5px 10px;
    border-radius: 8px;
    color: var(--input-text);
    right: 0;
    line-height: 30px;
    top: -40px;
    white-space: nowrap;
    font-size: 18px;
    font-weight: bold;
}
`
