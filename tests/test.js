const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const HTML = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const KEY = 'dapurRun.v1';
let pass = 0, fail = 0;
const ok = (c, m) => { c ? pass++ : (fail++, console.log('  ✗ FAIL: ' + m)); };
const section = m => console.log('\n' + m);
function boot(seed) {
  return new JSDOM(HTML, { runScripts: 'dangerously', url: 'https://local.test/',
    pretendToBeVisual: true, beforeParse(w) { if (seed) w.localStorage.setItem(KEY, seed); } });
}
const $ = (d, s, r) => (r || d.window.document).querySelector(s);
const $$ = (d, s, r) => [...(r || d.window.document).querySelectorAll(s)];
const click = (d, e) => e.dispatchEvent(new d.window.MouseEvent('click', {bubbles:true, cancelable:true}));
const typeIn = (d, e, v) => { e.value = v; e.dispatchEvent(new d.window.Event('input', {bubbles:true})); };
const tick = ms => new Promise(r => setTimeout(r, ms || 300));

(async function () {
let d = boot(null);
const item = i => $$(d, '.item')[i];
const named = n => $$(d, '.item').find(e => e.querySelector('.nm').textContent === n);

section('1. Clearing a quantity releases an item that typing had ticked');
let a = item(0);
typeIn(d, a.querySelector('.q'), '3');
ok(a.classList.contains('on'), 'typing a quantity ticks the item');
ok($(d, '#tally').textContent === '1', 'tally counts it');
typeIn(d, a.querySelector('.q'), '');
ok(!a.classList.contains('on'), 'clearing the quantity unticks it again');
ok($(d, '#tally').textContent === '0', 'tally back to zero');
ok(a.querySelector('.q').value === '', 'the box is empty');

section('2. Clearing works the same on an item you ticked by hand');
let b = item(1);
click(d, b.querySelector('.box'));
ok(b.classList.contains('on'), 'ticked by hand');
typeIn(d, b.querySelector('.q'), '2');
typeIn(d, b.querySelector('.q'), '');
ok(!b.classList.contains('on'), 'clearing the quantity takes it off the list too');
ok($(d, '#tally').textContent === '0', 'tally back to zero');

section('2b. An item ticked in an older version still clears');
const legacyId = item(2).dataset.id;
const d0 = boot(JSON.stringify({sel:{[legacyId]:1}, qty:{[legacyId]:'2'}}));
const leg = $$(d0, '.item').find(e => e.dataset.id === legacyId);
ok(leg.classList.contains('on') && leg.querySelector('.q').value === '2', 'restored ticked with its quantity');
typeIn(d0, leg.querySelector('.q'), '');
ok(!leg.classList.contains('on'), 'clearing it unticks it, even without the newer bookkeeping');
ok($(d0, '#tally').textContent === '0', 'and it leaves the tally');

section('2c. Ticking without ever typing is untouched');
const q2 = item(3);
click(d, q2.querySelector('.box'));
ok(q2.classList.contains('on'), 'an item ticked with no quantity stays ticked');
click(d, q2.querySelector('.box'));

section('3. Unticking clears the quantity and stock it held');
let c = item(4);
click(d, c.querySelector('.box'));
typeIn(d, c.querySelector('.q'), '4');
typeIn(d, c.querySelector('.s'), '1');
click(d, c.querySelector('.box'));                       // untick
ok(!c.classList.contains('on'), 'unticked');
ok(c.querySelector('.q').value === '' && c.querySelector('.s').value === '',
   'quantity and stock boxes are emptied, got q=' + c.querySelector('.q').value + ' s=' + c.querySelector('.s').value);
await tick();
let st = JSON.parse(d.window.localStorage.getItem(KEY));
ok(!st.qty[c.dataset.id] && !st.stk[c.dataset.id], 'and nothing is left in storage');

section('4. Clear all wipes the numbers too');
[item(5), item(6)].forEach(e => { typeIn(d, e.querySelector('.q'), '5'); });
click(d, $(d, '#clrall'));
ok($(d, '#tally').textContent === '0', 'everything unticked');
ok($$(d, '.item .q').every(e => e.value === ''), 'every quantity box is empty');
ok($$(d, '.item .s').every(e => e.value === ''), 'every stock box is empty');

section('5. Category Clear wipes the numbers too');
const cat0 = $(d, '.cat');
typeIn(d, $(d, '.item .q', cat0), '7');
click(d, [...cat0.querySelectorAll('.mini')].find(x => x.dataset.act === 'clear'));
ok($(d, '.item .q', cat0).value === '', 'category clear empties the quantity');

section('6. Adding your own item');
d = boot(null);
const forms = $$(d, '.additem');
ok(forms.length === 15, 'every category has an add box, got ' + forms.length);
const vegForm = $(d, '.additem[data-key="veg"]');
typeIn(d, $(d, 'input', vegForm), '  Petai   segar ');
vegForm.dispatchEvent(new d.window.Event('submit', {bubbles:true, cancelable:true}));
const mine = named('Petai segar');
ok(!!mine, 'the item appears in the checklist with whitespace tidied');
ok(mine.closest('.cat').dataset.key === 'veg', 'in the category it was added to');
ok(mine.classList.contains('on'), 'and it is ticked ready to shop');
ok($(d, '#tally').textContent === '1', 'counted in the tally');
ok($(d, '.bsel', mine.closest('.cat')).textContent === '1', 'counted in the category badge');
ok(mine.querySelector('img.thumb').getAttribute('src').startsWith('data:image/jpeg'),
   'it gets its own picture tile until you replace it');
ok($(d, 'input', vegForm).value === '', 'the add box empties, ready for the next one');
ok(mine.compareDocumentPosition($(d, '.additem[data-key="veg"]')) & 4,
   'it sits above the add box, at the end of the category');

section('7. Your item behaves like any other');
typeIn(d, mine.querySelector('.q'), '2');
ok(mine.querySelector('.q').value === '2', 'takes a quantity');
click(d, mine.querySelector('.nm'));
ok(!mine.classList.contains('on'), 'name click unticks it');
click(d, mine.querySelector('img.thumb'));
ok(mine.classList.contains('on'), 'photo click ticks it');
ok(mine.querySelector('.q').value === '', 'unticking cleared its quantity, like any other item');
typeIn(d, mine.querySelector('.q'), '2');
typeIn(d, $(d, '#search'), 'petai');
ok($$(d, '.item').filter(e => !e.hidden).length === 1, 'search finds it');
click(d, $(d, '#searchclr'));
click(d, $(d, '#makelist'));
ok($$(d, '#listbody tbody tr:not(.grouprow)').some(r => r.querySelector('.nm2').textContent === 'Petai segar'),
   'it reaches the shopping list');
click(d, $(d, '#tobought'));
ok($$(d, '#boughtbody tbody tr:not(.grouprow)').some(r => r.querySelector('.nm2').textContent === 'Petai segar'),
   'and the What I Bought page');
typeIn(d, $$(d, '#boughtbody .pinput')[0], '6.40');
ok($(d, '#boughtsum').textContent.trim() === 'RM 6.40', 'its price counts in the total');

section('8. Your item survives a refresh');
await tick();
const saved = d.window.localStorage.getItem(KEY);
const d2 = boot(saved);
const mine2 = $$(d2, '.item').find(e => e.querySelector('.nm').textContent === 'Petai segar');
ok(!!mine2, 'it is rebuilt after a refresh');
ok(mine2.classList.contains('on'), 'still ticked');
ok(mine2.querySelector('.q').value === '2', 'quantity kept');
ok($$(d2, '.item').length === 164, 'exactly one extra item, got ' + $$(d2, '.item').length);
ok($(d2, '.additem[data-key="veg"] input').value === '', 'the add box is clean');

section('9. Removing your own item');
d = boot(saved);
const m3 = $$(d, '.item').find(e => e.querySelector('.nm').textContent === 'Petai segar');
click(d, m3.querySelector('.editphoto'));
let pop = $(d, '.pop');
ok(!!pop && !!$(d, '[data-act="del"]', pop), 'your own item offers Remove this item');
d.window.confirm = () => true;
click(d, $(d, '[data-act="del"]', pop));
ok(!$$(d, '.item').find(e => e.querySelector('.nm').textContent === 'Petai segar'), 'it is gone');
ok($$(d, '.item').length === 163, 'back to the 163 listed items');
ok($(d, '#tally').textContent === '0', 'and out of the tally');
await tick();
const st9 = JSON.parse(d.window.localStorage.getItem(KEY));
ok(!(st9.custom || []).length, 'removed from storage too');

section('10. A listed item offers no Remove option');
click(d, $(d, '.item .editphoto'));
pop = $(d, '.pop');
ok(!!pop && !$(d, '[data-act="del"]', pop), 'the 163 listed items cannot be deleted by accident');

section('11. Empty submissions are ignored');
d = boot(null);
const f2 = $(d, '.additem[data-key="dry"]');
typeIn(d, $(d, 'input', f2), '   ');
f2.dispatchEvent(new d.window.Event('submit', {bubbles:true, cancelable:true}));
ok($$(d, '.item').length === 163, 'blank input adds nothing');
typeIn(d, $(d, 'input', f2), '<img src=x onerror=alert(1)>');
f2.dispatchEvent(new d.window.Event('submit', {bubbles:true, cancelable:true}));
const risky = $$(d, '.item').find(e => e.dataset.id.startsWith('mine-'));
ok(!!risky, 'an awkward name is still accepted');
ok(risky.querySelector('.nm').textContent === '<img src=x onerror=alert(1)>', 'kept as literal text');
ok(risky.querySelectorAll('img').length === 1, 'no markup is injected, got ' + risky.querySelectorAll('img').length);

section('12. Nothing external is loaded');
ok(!/https?:\/\//.test(HTML.replace(/base64,[A-Za-z0-9+/=]+/g, '')), 'no http(s) references');
ok(/data:font\/woff2/.test(HTML), 'fonts still embedded');
const jpegs = (fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8')
  .match(/data:image\/jpeg;base64,/g) || []).length;
ok(jpegs === 164, 'all 163 photos plus the fallback tile are embedded, got ' + jpegs);

console.log('\n' + '─'.repeat(46));
console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
})();
