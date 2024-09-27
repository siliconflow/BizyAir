// Open a new window for the OAuth
export const openOAuthPopup = async (setKey) => {
  const clientId = 'SFaJLLq0y6CAMoyDm81aMu';
  const ACCOUNT_ENDPOINT = 'https://account.siliconflow.cn';
  const authUrl = `${ACCOUNT_ENDPOINT}/oauth?client_id=${clientId}`;
  const popup = window.open(authUrl, 'oauthPopup', 'width=600,height=600');
  window.addEventListener('message', (event) => {
      if (event.data.length > 0 && event.data[0]['secretKey'] !== undefined) {
          setKey(event.data[0]['secretKey']);
      }
      popup.close();
  });
  window.postMessage
}
