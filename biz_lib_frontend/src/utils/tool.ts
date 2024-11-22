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
  
  const KB = 1024;
  const MB = KB * 1024;
  const GB = MB * 1024;

  if (size >= GB) {
    return (size / GB).toFixed(2) + 'G';
  } else if (size >= MB) {
    return (size / MB).toFixed(2) + 'MB';
  } else if (size >= KB) {
    return (size / KB).toFixed(2) + 'KB';
  } else {
    return size.toFixed(2) + 'B';
  }
}
