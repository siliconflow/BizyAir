export const styleMenus = `
.comfy-floating-button {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: auto;
    height: 32px;
    border-radius: 4px;
    background: #7C3AED;
    display: flex;
    padding: 0px 0 0 4px;
}
.bizyair-logo{
    width: 28px;
    height: 32px;
    margin: 0;
    padding: 0;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAAQwSURBVHic7ZwxiFxVFIb/KyuskCLFFtNpsUIKiwgWEVKslREiWERIIOAKlhYRUgRstlC0EEQsRBKIjaQWi11IkYiCSBZslBVmIEKEWVBQ2IUtZuGzeG/g+Zz39t1z78zszL0fLAvLeeec+efed887796VMplMJpPJZDKZTCaTSQsX6gAgRiKR2Jc0kPSDpB3n3HfTDrhsAtYZSPpA0tfOueNpBFh2AcfsSrrmnBvEdpyKgJJ0KOlN59xOTKcpCShJx5JejyliagJKxUh8MdZ0fiqGkwXjjKR7wEoMZykKKEkvSboew1GKU3jMwDn3fKiTVEegJK0DG6FOUhZQkl4NdZC6gBdCHcxSwENJr7kWJD0t6avSfl/SM232E669VsbpyrmYH9AE3blygp8e8GPF/qYxn5seOc1/AeyY5wg40+LjHDCs2P8NnDXksgr0ZyngrKbwL865iVMLuCjpgaRe5c+fOef+McS5JWndw37fECMuHb/o2w3XXgQOarZHwJohj/XyWh8ehH7+WY3AX+t/AM5L2lbxaFXlS+fcX4YYX0ha9bzmJ0OcuHT8pi/Vrlnnv/e86ujrNcVqyeGq58gbsxFNCCsdE32uYr8G7DXY3THEPws8MYjXjyqElQ6JHlVsV4D7TXbYRt+nBvEANqMKYaVDov2K7VaL3ceG2C9QlEi+PCJSOyuYDsneL+0utdhY677vDeIdAD6lznTpkPBdYIP/lytVvJ86gOsG8UbUFrS50yHpIe3TbAh4lR8UC8ekVbyNg1MnnuT1LNzEpiGm78LxiNM0basEireH580cv4WjD2z6xvBh3ivRe4YdA5+rOe99Sb+peMLYcc49DMitE/NsqH7j+34WuCpp4wSzFUmUP6cf49Q9ovJ00jHOKvDYM04feGuaUzgYo4BbhjjvG2PBki0ij/EvW3q015HbHeIuTRnzhiHG3RZ/VygK9S4sZCFdZdvg/zzNZctWabPpkcPCPcqNObIkTnP3ZodyccD//rhQzYQxtwy+mxoQT6i0/YHbngLCArWzAH7G8I2X19U5AC7U7CxdmYVpqI4o3n/4+p3UbRkBlyfY/mkQEBakpb9l8LnC5Pe770ywXTOKB/BRFBFCOCHBPTxrvtLnpFX1RoNt1xJmEsGvNYNpSW5E7V7V0V999I2axCvtbwQIOAz79BFoSe4To7/q6Btx8p6aewECzr/h0JKb984nitE37jQPKbZ9tNn3sC8gUQScZjH5LfCuiv5cVy6r2CPzu4o9zH8AzzbYrkm6U/62Erw3JuU90pL00Dn3SoiD1HeoBu+NSV3A4BNLKU/hfMwhkA9jOEl1BO5KejnGGeIUBcyHDQM4VnFmONrB65QEPFTks8JSOgLuqpi2UcWTll/AgaS3VSwY0f9fgjT/vTGxmfnemEwmk8lkMplMJpPJZFLjXzMoB90iULCqAAAAAElFTkSuQmCC) no-repeat center center;
    background-size: 28px 28px;
}
.menus-item{
    line-height: 32px;
    padding: 0 8px 0 32px;
    font-size: 14px;
    cursor: pointer;
    position: relative;
    background-size: 18px 18px;
    background-repeat: no-repeat;
    transition: background-color 0.4s;
    background-position: 8px center;
    margin: 0 4px;
}
.menus-item:hover{
    background-color: #4A238E;
}
.menus-item:hover .menus-item-arrow{
    opacity: 0;
}
.menus-item-example{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M0 3.75A.75.75 0 0 1 .75 3h7.497c1.566 0 2.945.8 3.751 2.014A4.5 4.5 0 0 1 15.75 3h7.5a.75.75 0 0 1 .75.75v15.063a.75.75 0 0 1-.755.75l-7.682-.052a3 3 0 0 0-2.142.878l-.89.891a.75.75 0 0 1-1.061 0l-.902-.901a3 3 0 0 0-2.121-.879H.75a.75.75 0 0 1-.75-.75Zm12.75 15.232a4.5 4.5 0 0 1 2.823-.971l6.927.047V4.5h-6.75a3 3 0 0 0-3 3ZM11.247 7.497a3 3 0 0 0-3-2.997H1.5V18h6.947c1.018 0 2.006.346 2.803.98Z'/%3E%3C/svg%3E");
}
.menus-item-key{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='m10.758 11.828l7.849-7.849l1.414 1.414l-1.414 1.415l2.474 2.474l-1.414 1.415l-2.475-2.475l-1.414 1.414l2.121 2.121l-1.414 1.415l-2.121-2.122l-2.192 2.192a5.002 5.002 0 0 1-7.708 6.293a5 5 0 0 1 6.294-7.707m-.637 6.293A3 3 0 1 0 5.88 13.88a3 3 0 0 0 4.242 4.242'/%3E%3C/svg%3E");
}
.menus-item-profile{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ddd' d='M15.71 12.71a6 6 0 1 0-7.42 0a10 10 0 0 0-6.22 8.18a1 1 0 0 0 2 .22a8 8 0 0 1 15.9 0a1 1 0 0 0 1 .89h.11a1 1 0 0 0 .88-1.1a10 10 0 0 0-6.25-8.19M12 12a4 4 0 1 1 4-4a4 4 0 0 1-4 4'/%3E%3C/svg%3E");
}
.menus-item-model{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath fill='%23fff' d='m222.72 67.9l-88-48.17a13.9 13.9 0 0 0-13.44 0l-88 48.18A14 14 0 0 0 26 80.18v95.64a14 14 0 0 0 7.28 12.27l88 48.18a13.92 13.92 0 0 0 13.44 0l88-48.18a14 14 0 0 0 7.28-12.27V80.18a14 14 0 0 0-7.28-12.28M127 30.25a2 2 0 0 1 1.92 0L212.51 76L128 122.24L43.49 76ZM39 177.57a2 2 0 0 1-1-1.75V86.66l84 46V223Zm177.92 0L134 223v-90.36l84-46v89.16a2 2 0 0 1-1 1.77Z'/%3E%3C/svg%3E");
}
.menus-item-news{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cg fill='none' stroke='%23fff' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5'%3E%3Cpath d='M4 21.4V2.6a.6.6 0 0 1 .6-.6h11.652a.6.6 0 0 1 .424.176l3.148 3.148A.6.6 0 0 1 20 5.75V21.4a.6.6 0 0 1-.6.6H4.6a.6.6 0 0 1-.6-.6M8 10h8m-8 8h8m-8-4h4'/%3E%3Cpath d='M16 2v3.4a.6.6 0 0 0 .6.6H20'/%3E%3C/g%3E%3C/svg%3E");
}
.menus-item-arrow{
    position: absolute;
    width: 16px;
    height: 16px;
    right: -2px;
    bottom: -2px;
    opacity: 1;
    transition: opacity 0.4s;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAACbSURBVFiF7ZYhEsIwFERfOpFIBAJZgeQoCG7CcThKy2lqEByhM4tIDSBIQyiIfS4z+X9fVBYqIilK2tTcOSd8J2lQopMUlxY465FjzlxT0aF9Oq+WFijCAhawgAUsYIGfC0RIZQI48fqlzmFfJDA1lw7YfhBeTAOsvxQ+ZgmEEK7ApXL4DehzLgZIbRY4kFmj3jAC/fQwY4z5f+5uET1JRps4hQAAAABJRU5ErkJggg==) no-repeat right bottom;
    background-size: 12px 12px;
}
.cmfy-floating-button-closer{
    width: 32px;
    height: 32px;
    cursor: pointer;
    transition: background-color 0.4s;
    transition: all 0.4s;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M7 4a1 1 0 0 1 1 1v6.333l10.223-6.815a.5.5 0 0 1 .777.416v14.132a.5.5 0 0 1-.777.416L8 12.667V19a1 1 0 1 1-2 0V5a1 1 0 0 1 1-1m10 3.737L10.606 12L17 16.263z'/%3E%3C/svg%3E") center center no-repeat;
    background-size: 16px 16px;
    border-radius: 0 4px 4px 0;
}
.cmfy-floating-button-closer:hover{
    background-color: #4A238E;
}
.cmfy-floating-button-closer-overturn{
    transform: rotate(180deg);
}
.bizyair-menu{
    width: 450px;
    padding-left: 4px;
    overflow: hidden;
    transition: width 0.4s ease;
    display: flex;
}
.bizyair-menu strong{
    font-size: 16px;
    color:#FFF;
    margin-right: 10px;
    line-height: 32px;
}
.bizyair-menu-item{
    display: flex;
}
.bizyair-menu-hidden{
    width: 0;
    padding-left: 0;
}
.comfy-floating-button-hidden{
    padding-left: 2px;
    padding-right: 2px;
}
.comfy-floating-button-hidden .cmfy-floating-button-closer{
    width: 0;
    margin: 0;
}
.comfy-floating-button-hidden:hover{
    padding-right: 0;
}
.comfy-floating-button-hidden:hover .cmfy-floating-button-closer{
    width: 32px;
    border-radius: 4px 0 0 4px;
}
`
