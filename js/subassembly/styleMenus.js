export const styleMenus = `
.comfy-floating-button {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: auto;
    height: 48px;
    border-radius: 8px;
    background: linear-gradient(270deg, #6262DE 0%, #7C3AED 100%);
    display: flex;
    padding: 4px 8px;
}
.bizyair-logo{
    width: 120px;
    height: 40px;
    line-height: 40px;
    margin: 0;
    padding: 0;
    display: flex;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;

    padding-left: 42px;
    font-size: 24px;
    margin-left: 4px;
    font-weight: 700;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAAQwSURBVHic7ZwxiFxVFIb/KyuskCLFFtNpsUIKiwgWEVKslREiWERIIOAKlhYRUgRstlC0EEQsRBKIjaQWi11IkYiCSBZslBVmIEKEWVBQ2IUtZuGzeG/g+Zz39t1z78zszL0fLAvLeeec+efed887796VMplMJpPJZDKZTCaTSQsX6gAgRiKR2Jc0kPSDpB3n3HfTDrhsAtYZSPpA0tfOueNpBFh2AcfsSrrmnBvEdpyKgJJ0KOlN59xOTKcpCShJx5JejyliagJKxUh8MdZ0fiqGkwXjjKR7wEoMZykKKEkvSboew1GKU3jMwDn3fKiTVEegJK0DG6FOUhZQkl4NdZC6gBdCHcxSwENJr7kWJD0t6avSfl/SM232E669VsbpyrmYH9AE3blygp8e8GPF/qYxn5seOc1/AeyY5wg40+LjHDCs2P8NnDXksgr0ZyngrKbwL865iVMLuCjpgaRe5c+fOef+McS5JWndw37fECMuHb/o2w3XXgQOarZHwJohj/XyWh8ehH7+WY3AX+t/AM5L2lbxaFXlS+fcX4YYX0ha9bzmJ0OcuHT8pi/Vrlnnv/e86ujrNcVqyeGq58gbsxFNCCsdE32uYr8G7DXY3THEPws8MYjXjyqElQ6JHlVsV4D7TXbYRt+nBvEANqMKYaVDov2K7VaL3ceG2C9QlEi+PCJSOyuYDsneL+0utdhY677vDeIdAD6lznTpkPBdYIP/lytVvJ86gOsG8UbUFrS50yHpIe3TbAh4lR8UC8ekVbyNg1MnnuT1LNzEpiGm78LxiNM0basEireH580cv4WjD2z6xvBh3ivRe4YdA5+rOe99Sb+peMLYcc49DMitE/NsqH7j+34WuCpp4wSzFUmUP6cf49Q9ovJ00jHOKvDYM04feGuaUzgYo4BbhjjvG2PBki0ij/EvW3q015HbHeIuTRnzhiHG3RZ/VygK9S4sZCFdZdvg/zzNZctWabPpkcPCPcqNObIkTnP3ZodyccD//rhQzYQxtwy+mxoQT6i0/YHbngLCArWzAH7G8I2X19U5AC7U7CxdmYVpqI4o3n/4+p3UbRkBlyfY/mkQEBakpb9l8LnC5Pe770ywXTOKB/BRFBFCOCHBPTxrvtLnpFX1RoNt1xJmEsGvNYNpSW5E7V7V0V999I2axCvtbwQIOAz79BFoSe4To7/q6Btx8p6aewECzr/h0JKb984nitE37jQPKbZ9tNn3sC8gUQScZjH5LfCuiv5cVy6r2CPzu4o9zH8AzzbYrkm6U/62Erw3JuU90pL00Dn3SoiD1HeoBu+NSV3A4BNLKU/hfMwhkA9jOEl1BO5KejnGGeIUBcyHDQM4VnFmONrB65QEPFTks8JSOgLuqpi2UcWTll/AgaS3VSwY0f9fgjT/vTGxmfnemEwmk8lkMplMJpPJZFLjXzMoB90iULCqAAAAAElFTkSuQmCC) no-repeat 0 center;
    background-size: 40px 40px;
}
.menus-item{
    line-height: 40px;
    padding: 0 16px 0 42px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 8px;
    position: relative;
    font-weight: blod;
    background-zise: 18px 18px;
    background-repeat: no-repeat;
    transition: background-color 0.4s;
    background-position: 16px center;
    margin: 0 4px;
}
.menus-item:hover{
    background-color: #4A238E;
}
.menus-item:hover .menus-item-arrow{
    opacity: 0;
}
.menus-item-example{
    background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAADaSURBVDiN7ZOxSgNBGIS/XyxiYZdeH0BIa3lW5mEiljaWNnZJl0cxVdpAylgGRLC0szCF8FlkT4/lblUIqRxYdtiZnflhWdgRQu0B18BRpr0Bs4h4BFDPgEvgOPO9A5NQK2BeKLtL+23Bc4FauUXVVNS+OvUbU7Wfeb7uHnRVRMQrMAJe0hqls1YcFsYlIj7Udc1L3s6J/or/oD0GNZ9/oJrpzzVRT4GTTB80gzaJjzvKav2pMNAmUts50GsxDIGbxO+Bh9aQiEWhZAt1pS5/8hW/SMLVLzy7wyeDumC8BnR73wAAAABJRU5ErkJggg==)
}
.menus-item-key{
    background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAAEISURBVDiNrZKtbgJBFIXPNAjEihUVCETlJrU8QgWiEoHkARAVfQAkkqSPgek7UElCk75AHbKbIFd8iB6SybDL0i43meRm7p1vzv2ROhhQAP0uDAEToAJebgH5ALKuEIDNv0CJkpn9zZ/6FEH2QObz5bui7kEOPAKDBgjAm5VUwCQFDIB1VD/+cRE3Flg51gjZAwdgaQVzg07ALMp/BZ7rylkbUiT3fZfwA+RtTcwsc9kQH1nV9BLnTtJQUk/SZ11CCGFr93wyCai0f9+gaGi3rIunyTs39GyxPOoKeLgG9BRt6eikxBCAVSskgk09ndgq702v7X1IYLmksX4bW0p6DyF8X63mFnYEH/d1WyHH6EgAAAAASUVORK5CYII=)
}
.menus-item-model{
    background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAAFFSURBVDiNpZQxasNAEEW/hEoXKnSEFC5cuM0B3DmQA+QILgL2AVymj8E+QG6gwoUMThFI6cIXSBFICoNdBmJ4KTKbDJIsxWRhQDvz583u7K6klgH0gF6brg1Q8DuKs4BABsyBT2AP3JrtzTcHsiZAAoxdwgxIXTw1XygwBpIyJAU2toUcuGgo2AWWpt2EYrHFbyT1JX1IepL02rD7F0mPpu1b7g8o7Hkl6U7SFhjWrGYoaWualc+NvTCKoitJA0lHSbmdVNeskJTbSgamrVSaArh5Aoxc40ODR77B1qepJCUV6vfKjpJmwIOkZ3NfRlF0qNOfBDngAXgP303auCl4zgignSQB139NdNqdd3bchVwCXRdbA2s3L1/ITrlCAkzcSd3bjV+bpeYLJzipPJESMAMWLuHNLBRYND7aGuD/fiMngK2ALwOqjs76pY59AAAAAElFTkSuQmCC)
}
.menus-item-news{
    background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAADuSURBVDiN7ZQxTgJBGIW/ZygsOAilCVuSaGfsPApWNBbeYI9AvIUdFDQkHsASexI0MZHC5FkwkFn4Z1d6v2ZnM/u//73ZmREZtvvAkJitpGVhriFS2d64nbpU38vGE2AL3KVnzhVQA2PbSHpoczSzPSvM3SRHi5KzXlTYwiNwHzk7V6gGPoCfJPYp6QngIvra9jRF+LY9AN6AlyQCsEjj6y5Hz8A7u0VfSdr/hLxZYz1DIUlzYF7KF9EVLWIa1XRFiwid/kfrJhdaAyPbt5we2mMugQG7jdnkj9dIzsZ2dUhxJNYHqpMuMa+SvvYvv1/Z/UbNb3dBAAAAAElFTkSuQmCC)
}
.menus-item-arrow{
    position: absolute;
    width: 16px;
    height: 16px;
    right: -2px;
    bottom: 0;
    opacity: 1;
    transition: opacity 0.4s;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAABRSURBVEiJ7cyxDYAwDETRL8QQEXVmoIH9B8gkpKE9FnAkiyjdvdJnfTBbRlKVdGR+tx/9GzhXxdMcD+2jQVIFrmAqwDMVB16gB/cOtEzczCZ9sVgOy9qtdcwAAAAASUVORK5CYII=) no-repeat;
}
.cmfy-floating-button-closer{
    width: 30px;
    height: 30px;
    cursor: pointer;
    transition: background-color 0.4s;
    border-radius: 8px;
    margin: 5px 0 0 8px;
    transition: all 0.4s;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAADNSURBVDiNzZIhDsJQEETfNggEh+ASTRA0QVTADRAI7gCGE4DgECQcoiHBVdZwhHosggSSQfSTlNJ+ioJVf//Ozu5MFv4mJPUkDT9gYklnSaO64lSSPM1LSTcVMX/+ByVM17PZHlgDq2o9eG95ae4DKTAGJma2bU0gKQYyl4ZmdqzD1RI4jQlwACIzy5sGeSUAjaZ6CcxsB0wotKfOi+82cJpDl2bOk/YEjiQHIgovEkmLKqZTel+Bew3JBZhJOgGbxmnuYAa+jbyn/LN4ACZQZ8GumOyLAAAAAElFTkSuQmCC) no-repeat center center;
}
.cmfy-floating-button-closer:hover{
    background-color: #4A238E;
}
.cmfy-floating-button-closer-overturn{
    transform: rotate(180deg);
}
.bizyair-menu{
    width: 478px;
    padding-left: 10px;
    overflow: hidden;
    transition: width 0.4s ease;
}
.bizyair-menu-item{
    display: flex;
    width: 476px;
}
.bizyair-menu-hidden{
    width: 0;
    padding-left: 0;
}
`