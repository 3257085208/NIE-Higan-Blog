export function initEasterEggs(state) {
  console.log(
    '%c Higan %c v1.2.3 %c 这里刻下了我十八岁时的偏执与热爱 ',
    'color:#fff;background:#1a202c;padding:5px 10px;border-radius:5px 0 0 5px;font-weight:bold',
    'color:#fff;background:#00b894;padding:5px 10px;font-weight:bold',
    'color:#666;background:#f2f3f5;padding:5px 10px;border-radius:0 5px 5px 0'
  );
  console.log('%c 彩蛋提示：在控制台输入 love() 或在键盘按下 n-i-e 试试看 ', 'color:#999;font-size:11px');

  window.love = () => {
    const messages = [
      '❤️ 青春万岁！如果你也热爱折腾，我们就是同路人。',
      '✨ 这一行行代码，是我留给十八岁的证据。',
      '🚀 所谓最伟大的作品，就是每一个不曾起舞的日子，都没有辜负自己。'
    ];
    console.log(`%c ${messages[Math.floor(Math.random() * messages.length)]}`, 'color:#e91e63;font-size:16px;font-weight:bold');
    alert('这，就是我最伟大的作品。—— Higan');
  };

  if (state._eggInited) return;
  state._eggInited = true;
  let seq = '';
  window.addEventListener('keydown', event => {
    if (event.key.length !== 1) return;
    seq = (seq + event.key.toLowerCase()).slice(-3);
    if (seq !== 'nie') return;
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,184,148,0.1);z-index:99999;pointer-events:none;transition:all 0.5s';
    document.body.appendChild(overlay);
    document.documentElement.style.filter = 'invert(1) hue-rotate(180deg) contrast(1.2)';
    setTimeout(() => {
      document.documentElement.style.filter = 'none';
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 500);
      seq = '';
    }, 3000);
  });
}

