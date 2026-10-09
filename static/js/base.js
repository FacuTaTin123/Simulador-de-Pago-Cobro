document.addEventListener('DOMContentLoaded', () => {
  const number = document.querySelector('#numero');
  if (!number) return;
  const holder = document.querySelector('#titular');
  const expiry = document.querySelector('#vencimiento');
  const cvv = document.querySelector('#cvv');

  number.addEventListener('input', () => {
    const digits = number.value.replace(/\D/g, '').slice(0, 19);
    number.value = digits.replace(/(.{4})/g, '$1 ').trim();
  });
  holder.addEventListener('input', () => {
    holder.value = holder.value.replace(/[^A-Za-zÀ-ÿ .'-]/g, '');
  });
  expiry.addEventListener('input', () => {
    const digits = expiry.value.replace(/\D/g, '').slice(0, 4);
    expiry.value = digits.length > 2 ? `${digits.slice(0, 2)}/${digits.slice(2)}` : digits;
  });
  cvv.addEventListener('input', () => { cvv.value = cvv.value.replace(/\D/g, '').slice(0, 4); });
});
