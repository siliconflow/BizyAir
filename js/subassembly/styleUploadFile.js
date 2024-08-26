export const styleUploadFile = `
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
.cm-input-file-modle {
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
.cm-file-list{
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
.cm-input-item{
    height: 30px;
    margin-bottom: 10px;
    padding: 0 10px;
}
select.cm-input-item{
    margin: 0 0 10px 0;
}
p.cm-input-item-error,
select.cm-input-item-error,
input.cm-input-item-error{
    border-color: var(--error-text);
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
}
.bizyair-model-list-item{
    width: 100%;
    display: flex;
    line-height: 40px;
    height: 40px;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);
}
.bizyair-model-list-label{
    flex: 1;
    width: 50%;
}
.bizyair-model-list-available{
    flex: 1;
    width: 50%;
}
`