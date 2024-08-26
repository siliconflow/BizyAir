export const styleExample = `
.example-menu {
    background-color: var(--comfy-menu-bg);
    filter: brightness(95%);
    will-change: transform;
    min-width: 100px;
    box-shadow: 0 0 10px black;
    padding: 10px;
    margin: 0;
}
.example-menu li {
    list-style: none;
    cursor: pointer;
    line-height: 1.5;
    padding: 0;
    margin: 4px 0;
    position: relative;
    padding-left: 20px;
}
.example-menu li.has-child::before {
    content: "▶";
    margin-right: 5px;
    transition: all 0.1s;
    position: absolute;
    left: 0;
    top: 0;
}
.example-menu li.has-child.show-child::before {
    transform: rotate(90deg);
}
.example-menu li .child-list {
    padding-left: 0px;
}
`