export const objectToArray = (obj: any) => {
    return Object.keys(obj).map(key => ({name: key, value: obj[key]}));
}

export const sliceString = (str: string, length: number) => {
  return str.length > length ? str.slice(0, length) + '...' : str;
}

export const formatNumber = (num: number | undefined) => {
  if (!num) {
    return '0';
  }
  if (num < 1000) {
    return num.toString();
  }
  return (num / 1000).toFixed(1) + 'k';
}

export const formatSize = (size: number | undefined) => {
  if (!size) {
    return '-';
  }
  return (size / 1024 / 1024 / 1024).toFixed(2) + 'G';
}
