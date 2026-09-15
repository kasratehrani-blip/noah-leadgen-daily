const { chromium } = require('playwright');
(async () => {
  const [,, inp, out] = process.argv;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium/chrome' }).catch(async () => chromium.launch());
  const pg = await b.newPage();
  await pg.goto('file://' + inp, { waitUntil: 'load' });
  await pg.pdf({ path: out, format: 'A4', printBackground: true, margin: { top: '14mm', bottom: '14mm', left: '14mm', right: '14mm' } });
  await b.close();
  console.log('PDF OK', out);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
