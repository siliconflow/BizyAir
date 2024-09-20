export const styleDialog = `
.bizyair-new-dialog{
    position: fixed;
    left: 0;
    top: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.6);
}
.bizyair-dialog-content{
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%) scale(1);
    padding: 20px;
    min-width: 400px;
    min-height: 120px;
    max-height: 80vh;
    max-width: 80vw;
    border-radius: var(--p-dialog-border-radius);
    box-shadow: var(--p-dialog-shadow);
    background: var(--p-dialog-background);
    border: 1px solid var(--p-dialog-border-color);
    color: var(--p-dialog-color);
}
.bizyair-new-dialog-title{
    font-size: 20px;
    line-height: 48px;
    font-weight: bold;
    margin: 0;
    padding: 0;
}
.bizyair-new-dialog-body{
    margin: 0 0 20px 0;
    overflow-y: auto;
}
.bizyair-new-dialog-footer{
    display: flex;
    justify-content: flex-end;
}
.bizyair-new-dialog-btn{
    color: var(--input-text);
    background-color: var(--comfy-input-bg);
    border-radius: 8px;
    border-color: var(--border-color);
    border-style: solid;
    fons-size: 20px;
    box-sizing: border-box;
    line-height: 30px;
    cursor: pointer;
    padding: 0 18px;
    margin-left: 10px;
}
.bizyair-new-dialog-btn:hover{
    background-color: var(--comfy-input-bg-hover);
}
.bizyair-new-dialog-icon{
    width: 64px;
    height: 64px;
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
    margin: 20px auto;
}
.bizyair-new-dialog-succeed{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 36 36'%3E%3Cpath fill='%2367c23a' d='M18 2a16 16 0 1 0 16 16A16 16 0 0 0 18 2m10.45 10.63L15.31 25.76L7.55 18a1.4 1.4 0 0 1 2-2l5.78 5.78l11.14-11.13a1.4 1.4 0 1 1 2 2Z' class='clr-i-solid clr-i-solid-path-1'/%3E%3Cpath fill='none' d='M0 0h36v36H0z'/%3E%3C/svg%3E");
}
.bizyair-new-dialog-warning{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 20 20'%3E%3Cpath fill='%23e6a23c' d='M10 2c4.42 0 8 3.58 8 8s-3.58 8-8 8s-8-3.58-8-8s3.58-8 8-8m1.13 9.38l.35-6.46H8.52l.35 6.46zm-.09 3.36c.24-.23.37-.55.37-.96c0-.42-.12-.74-.36-.97s-.59-.35-1.06-.35s-.82.12-1.07.35s-.37.55-.37.97c0 .41.13.73.38.96c.26.23.61.34 1.06.34s.8-.11 1.05-.34'/%3E%3C/svg%3E");
}
.bizyair-new-dialog-error{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 24 24'%3E%3Cpath fill='%23f56c6c' d='M12 4a8 8 0 1 0 0 16a8 8 0 0 0 0-16M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12m5.793-4.207a1 1 0 0 1 1.414 0L12 10.586l2.793-2.793a1 1 0 1 1 1.414 1.414L13.414 12l2.793 2.793a1 1 0 0 1-1.414 1.414L12 13.414l-2.793 2.793a1 1 0 0 1-1.414-1.414L10.586 12L7.793 9.207a1 1 0 0 1 0-1.414'/%3E%3C/svg%3E");
}
.bizyair-toast{
    position: fixed;
    right: 0;
    padding: 10px 0;
    border-radius: 8px 0 0 8px;
    z-index: 10000;
    display: flex;
    align-items: center;
    min-width: 240px;
    border: 1px solid #000;
    height: 40px;
    line-height: 40px;
}
.bizyair-toast-succeed{
    border-color: #67c23a;
    color: #67c23a;
    background-color: rgba(103, 192, 58, 0.2);
}
.bizyair-toast-warning{
    border-color: #dba44b;
    color: #dba44b;
    background-color: rgba(219, 164, 75, 0.2);
}
.bizyair-toast-error{
    border-color: #f56c6c;
    color: #f56c6c;
    background-color: rgba(245, 108, 108, 0.2);
}
.bizyair-toast-icon{
    width: 20px;
    height: 20px;
    margin: 0 10px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 36 36'%3E%3Cpath fill='%2367c23a' d='M18 2a16 16 0 1 0 16 16A16 16 0 0 0 18 2m10.45 10.63L15.31 25.76L7.55 18a1.4 1.4 0 0 1 2-2l5.78 5.78l11.14-11.13a1.4 1.4 0 1 1 2 2Z' class='clr-i-solid clr-i-solid-path-1'/%3E%3Cpath fill='none' d='M0 0h36v36H0z'/%3E%3C/svg%3E");
    background-size: 20px 20px;
}
.bizyair-toast-icon-warning{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 24 24'%3E%3Cpath fill='%23dba44b' d='M13 13h-2V7h2m0 10h-2v-2h2M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2'/%3E%3C/svg%3E")
}
.bizyair-toast-icon-error{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 24 24'%3E%3Cpath fill='%23f56c6c' d='M13 13h-2V7h2m0 10h-2v-2h2M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2'/%3E%3C/svg%3E");
}
.bizyair-toast-content{
    padding-right: 40px;
    flex: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}
.bizyair-toast-close{
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    cursor: pointer;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 24 24'%3E%3Cpath fill='%2367c23a' d='M3 16.74L7.76 12L3 7.26L7.26 3L12 7.76L16.74 3L21 7.26L16.24 12L21 16.74L16.74 21L12 16.24L7.26 21zm9-3.33l4.74 4.75l1.42-1.42L13.41 12l4.75-4.74l-1.42-1.42L12 10.59L7.26 5.84L5.84 7.26L10.59 12l-4.75 4.74l1.42 1.42z'/%3E%3C/svg%3E");
    background-size: 20px 20px;
    background-repeat: no-repeat;
}
.bizyair-toast-warning .bizyair-toast-close{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 48 48'%3E%3Cpath fill='none' stroke='%23dba44b' stroke-linecap='round' stroke-linejoin='round' stroke-width='4' d='m6 11l5-5l13 13L37 6l5 5l-13 13l13 13l-5 5l-13-13l-13 13l-5-5l13-13z' clip-rule='evenodd'/%3E%3C/svg%3E");
}
.bizyair-toast-error .bizyair-toast-close{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 24 24'%3E%3Cpath fill='%23f56c6c' d='M3 16.74L7.76 12L3 7.26L7.26 3L12 7.76L16.74 3L21 7.26L16.24 12L21 16.74L16.74 21L12 16.24L7.26 21zm9-3.33l4.74 4.75l1.42-1.42L13.41 12l4.75-4.74l-1.42-1.42L12 10.59L7.26 5.84L5.84 7.26L10.59 12l-4.75 4.74l1.42 1.42z'/%3E%3C/svg%3E")
}
`
