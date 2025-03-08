export const styleMenus = `
.comfy-floating-button {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: auto;
    height: 32px;
    border-radius: 4px;
    // background: #7C3AED;
    display: flex;
    // padding: 0px 0 0 4px;
    z-index: 999;
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
