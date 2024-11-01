export const objectToArray = (obj: any) => {
    return Object.keys(obj).map(key => ({name: key, value: obj[key]}));
}
