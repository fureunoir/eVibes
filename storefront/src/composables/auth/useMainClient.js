import { ref } from 'vue';

export function useMailClient() {
  const mailClientUrl = ref(null);

  const mailClients = {
    'gmail.com': 'https://mail.google.com/',
    'outlook.com': 'https://outlook.live.com/',
    'icloud.com': 'https://www.icloud.com/',
    'yahoo.com': 'https://mail.yahoo.com/'
  };

  function detectMailClient(email) {
    mailClientUrl.value = null;

    if (!email) return;

    const domain = email.split('@')[1];

    Object.entries(mailClients).forEach((el) => {
      if (domain === el[0]) mailClientUrl.value = el[1];
    });

    return mailClientUrl.value;
  }

  function openMailClient() {
    if (mailClientUrl.value) {
      window.open(mailClientUrl.value);
    }
  }

  return {
    mailClientUrl,
    detectMailClient,
    openMailClient
  };
}