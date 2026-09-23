// 投稿材料 Word 生成：编辑版大纲（新撰，非全文大纲复制）＋正文第1-10章原样收录
// 用法：node build-submission-docx.js
const fs = require('fs');
const path = require('path');
const docx = require('E:/npm/node_modules/docx');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType,
} = docx;

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = 'C:/Users/yuwen/Desktop/《重生2011：从被优化开始》投稿材料（大纲+正文1-10章）.docx';

const SONG = { ascii: 'Times New Roman', eastAsia: '宋体', hAnsi: 'Times New Roman' };
const HEI = { ascii: 'Arial', eastAsia: '黑体', hAnsi: 'Arial' };

function t(text, opts = {}) {
  return new TextRun({ text, font: SONG, size: 24, ...opts });
}
function bodyP(text) {
  return new Paragraph({
    spacing: { line: 360, lineRule: 'auto', after: 60 },
    indent: { firstLine: 480 },
    children: [t(text)],
  });
}
function richP(runs) {
  return new Paragraph({
    spacing: { line: 360, lineRule: 'auto', after: 60 },
    indent: { firstLine: 480 },
    children: runs,
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 200 },
    children: [new TextRun({ text, font: HEI, size: 32, bold: true })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 280 },
    children: [new TextRun({ text, font: HEI, size: 28, bold: true })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 100 },
    children: [new TextRun({ text, font: HEI, size: 26, bold: true })],
  });
}
function centerP(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 140 },
    children: [t(text, opts)],
  });
}
function spacer(n = 1) {
  return Array.from({ length: n }, () => new Paragraph({ children: [] }));
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ---------- 读取第1-10章 ----------
const chapters = [];
for (let i = 1; i <= 10; i++) {
  const file = path.join(ROOT, '正文', '卷一', `第${String(i).padStart(2, '0')}章.txt`);
  const raw = fs.readFileSync(file, 'utf8');
  const lines = raw.split(/\r?\n/).map(s => s.trim());
  const titleIdx = lines.findIndex(s => s.length > 0);
  const title = lines[titleIdx];
  const body = lines.slice(titleIdx + 1).filter(s => s.length > 0);
  chapters.push({ title, body });
}
const totalChars = chapters.reduce((s, c) => s + c.body.join('').replace(/\s/g, '').length, 0);
const wanZi = (totalChars / 10000).toFixed(1);

// ---------- 大纲内容（编辑版，新撰） ----------
const intro = [
  '“你的岗位，模型成本是你的十分之一。”',
  '2026年4月15日下午三点四十，陈序被优化了。三十七岁，房贷还剩89.4万，存款11.2万，十五年代码换来一个纸箱。',
  '当晚他喝断片。再睁眼，2011年7月17日，入职报到的前一天。',
  '兜里三百二十六块五。比特币还是十三块五美元一个，微信公众号还要一年才有。',
  '他下楼买了个黑皮笔记本，写下头一行：7.18，词峰会崩。',
  '词峰是他明天报到那家公司的招牌产品。这一行字准不准，下午三点见分晓。',
];

const synopsis = [
  '2026年4月15日，三十七岁的陈序被AI裁掉。HR当面给他算了笔账：他管的业务线原来十二个人，接上模型两个人就够跑，“你的岗位，模型成本是你的十分之一”。房贷还剩89.4万，存款11.2万。当晚他一个人喝到断片。',
  '再睁眼是2011年7月17日，入职报到的前一天。兜里三百二十六块五，脑子里装着往后十五年。他手里只有一个黑皮笔记本和一身真本事。隔天报到，下午三点公司主力产品全线白屏，他接下这活，通宵把系统救了回来。这一夜他十五年前也熬过，那次功劳记在了别人头上。这一次，有人在会上当众替他说了一句实话。几天后，他把全部家当押进一个所有人都说是骗局的东西里，两千八百八十块，三十二个币，成交后兜里只剩三十四块五。',
  '往后的路他一步一步走：抄底比特币，公众号上线当天注册，股灾前十天清仓，押注AI。前世抢他功劳的上司、看不懂他却肯信他的师父、凡事追问“逻辑链”的林见夏、把裁员名单递到他面前的零界创始人，一个个又走了回来。',
  '但记忆会折旧，风口也会改道。2022年往后，他脑子里只剩下大方向，具体哪家公司、哪一天，全都模糊了。没有答案的时候，他得证明自己还是自己。2026年4月15日会再来一次，那天签字的人是他。',
];

const volumes = [
  ['卷一《重回2011》（2011–2012）',
    '陈序在出租屋里醒来。头一天他还是个三十七岁的失业程序员，抱着纸箱走进雨里，喝到断片。醒来摸到的手机比他那部小了一圈，屏幕底下凸出来三颗键。\n隔天他去金杉软件报到。午后他去找副总监要活干，想接那摊没人管的在线版代码，被一句“真出了事，也轮不到一个刚报到的人往上顶”顶了回来。下午三点，公司主力产品词峰在线版全线白屏。日志指到入口文件第87行，全组四十多人往下追了三层就断了。代码是刚离职的人留的，几乎没有注释；重启、回滚都试过，没用。他站出来接了这活，通宵查到缓存那一层，对着手册抄了六页纸，天亮前把系统救了回来。十五年前这一夜他也熬过，功劳记在了别人头上。这一次他留了记录。\n副总监庞坚抢功成性，处处压他。他不争，只把事做实、留痕。大学四年攒下的两千九百块，他全换了比特币，三十二个，没人看得懂他在干什么。买完就开始跌，一路跌到年底，他反倒又凑钱补了两回。2011年底，他手里的比特币凑到了将近三百个，总成本不到八千块。\n2012年夏天事业部裁撤，庞坚把他的名字报了上去，排在头一个，和前世一模一样。前世他签了降级调岗才保住工号，这一次，名单当众翻了盘。他去了星浪；8月微信公众号上线，当天他注册了头一个号。'],
  ['卷二《风口》（2013–2014）',
    '他和死党袁野把公众号做成矩阵，粉丝破百万。比特币从几百涨到八千，所有人都说还能再翻十倍，他分三批清空了账户。五天后文件下来，全网腰斩。\n这一年他也头一回栽了跟头：记忆里那场大跌的日子，他记岔了一周，提前清仓被同行当笑话截图群发。一周后，那张截图成了封神图。\n年底他在京城买下两套房，一套写了父母的名字。林见夏从深城回来，进了公司。'],
  ['卷三《万众创业》（2014–2016）',
    '他辞职创业，三个人一间民房，做出海工具。两年后用户破千万、月流水千万级，也招来了巨头的抄袭和下架投诉。\n2015年A股疯牛，办公室人人满仓，他立下清仓纪律，被全公司笑作“老板踏空”。十天后5178点，千股跌停。'],
  ['卷四《庄家》（2016–2018）',
    '他从创业者转成投资人。投的那些公司里有一家叫零界科技，就是前世把他送上裁员名单的那家。'],
  ['卷五《黑天鹅与AI》（2019–2023）',
    '疫情、芯片、教培双减，他一次次躲开，“你为什么会知道”的追问也一次次逼近。\n2022年往后，他的记忆折旧到只剩大方向。也是在这一年，ChatGPT发布了，他早几年布下的AI仓位浮出水面。'],
  ['卷六《那个日子》（2024–2026）',
    '2026年4月15日，他坐在零界的董事会上。裁员方案摆在桌面，打头的部门就是算法组。前世的这一天，他抱着纸箱走进雨里。\n这一次他说：不裁一人。'],
];

// 卷四之后为规划走向，具体节点随连载调整。这行会原样印进投稿稿，是给编辑看的诚实交底。
const volumeNote = '卷一、卷二的节点已经细化到章。卷四往后还在想，大方向是这样，具体怎么落得看写到那儿再说。另外白屏那一夜我改了六遍。我自己干过这行，整栋楼就剩一个人亮着屏那种感觉，想写准。';

const persons = [
  ['陈序（男主）', '三十七岁上被AI裁掉，重回2011年报到前夜。技术过硬，谋定后动，认准了就敢下重注。手里一个黑皮笔记本，记着往后十五年的风口和账目。他手里攥着的只是记忆，而记忆会折旧、会记岔，越往后越不好使。'],
  ['林见夏（女主）', '产品经理，卷一第9章出场。不懂代码，懂逻辑也懂人。结论她不听，她只要推导过程。后来做到他的COO，也是全书唯一知道他底牌的人。感情线走得慢。'],
  ['庞坚（前世宿怨）', '词峰副总监，抢功成性。他倒也不坏，就是乌纱帽永远排在最前头，新人太亮，照出他的平庸。'],
];

// 其余人物（袁野、秦深、小满、陆见深、钱总等）卷二之后陆续出场，此处不列。
const personsNote = '其余人物卷二以后才出场，这里就不列了。';

// ---------- 信息表 ----------
function infoRow(k, v) {
  const cellOpts = { margins: { top: 90, bottom: 90, left: 140, right: 140 } };
  return new TableRow({
    children: [
      new TableCell({
        width: { size: 2200, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: 'F2F2F2' },
        ...cellOpts,
        children: [new Paragraph({ children: [t(k, { bold: true })] })],
      }),
      new TableCell({
        width: { size: 6800, type: WidthType.DXA },
        ...cellOpts,
        children: [new Paragraph({ children: [t(v)] })],
      }),
    ],
  });
}
const infoTable = new Table({
  columnWidths: [2200, 6800],
  rows: [
    infoRow('书名', '《重生2011：从被优化开始》'),
    infoRow('笔名', '沧海横笛'),
    infoRow('题材', '男频·都市·重生·互联网职场＋时代投资（无系统、无异能，重生记忆流）'),
    infoRow('预计篇幅', '六卷长线连载，卷一约40万字'),
    infoRow('单章字数', '2000–3000字'),
    infoRow('当前进度', `已完成第1—10章约${wanZi}万字，存稿在写`),
    infoRow('联系方式', 'QQ：290450146'),
  ],
});

// ---------- 组装 ----------
const children = [];

// ---------- 开头（朴素文档式，无封面页、无信息表） ----------
children.push(new Paragraph({
  spacing: { after: 120 },
  children: [new TextRun({ text: '《重生2011：从被优化开始》', font: HEI, size: 36, bold: true })],
}));
children.push(bodyP('沧海横笛　QQ：290450146'));
children.push(bodyP('男频都市重生。卷一约四十万字，第1—10章已完成，存稿在写。下面是简介、梗概、分卷和人物，正文附在后面。'));

children.push(h1('简介'));
intro.forEach(line => children.push(bodyP(line)));

children.push(h1('梗概'));
synopsis.forEach(p => children.push(bodyP(p)));

children.push(h1('分卷'));
volumes.forEach(([vt, vd]) => {
  children.push(h3(vt));
  vd.split('\n').forEach(seg => children.push(bodyP(seg)));
});
children.push(bodyP(volumeNote));

children.push(h1('人物'));
persons.forEach(([name, desc]) => {
  children.push(richP([t(name + '：', { bold: true }), t(desc)]));
});
children.push(bodyP(personsNote));


children.push(h1('正文（第1—10章）'));
children.push(bodyP(`以下是第1—10章原稿，连章未删节，合计约${wanZi}万字。`));

// 正文
chapters.forEach(ch => {
  children.push(pageBreak());
  children.push(h2(ch.title));
  ch.body.forEach(line => children.push(bodyP(line)));
});

const doc = new Document({
  creator: '沧海横笛',
  title: '《重生2011：从被优化开始》投稿材料',
  styles: {
    default: {
      document: {
        run: { font: SONG, size: 24 },
      },
    },
  },
  sections: [{ children }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('OK ->', OUT);
console.log('');
console.log('【R18 闸门·核对清单】正文已自动同步，但大纲文案是硬编码，须人工逐项核对：');
console.log('  [ ] 1. 卷一简介的事件顺序/技术口径 与 ch1-10 正文是否一致');
console.log('  [ ] 2. 数字口径（房贷89.4万/存款11.2万/现金326.5/月供7183.62/赔偿57.4万/');
console.log('         BTC首仓32个@¥90=¥2880、成交后兜里34.5卡里20、2011年末约296个成本¥7880）');
console.log('  [ ] 3. 人物介绍的口头禅与台词引用 是否与正文原句一致');
console.log('  [ ] 4. 章末钩子/卖点 是否已反映到简介与卷一段');
console.log('  [ ] 4b. 大纲文案里的章号引用 是否与当前逐章表一致（林见夏第9章/全仓BTC第10章）');
console.log('  [ ] 4c. 简介口径与《全书大纲》是否逐字一致（大纲为唯一事实源）：');
console.log('         python ai-tasks/scripts/check_intro_sync.py   ← 退出码须为0');
console.log('       （R32：本脚本的 intro 是衍生物，改它不算改，须同批回灌大纲）');
console.log('  [ ] 5. 大纲文案整体过机检（不是只核改动处）：');
console.log('         python ai-tasks/scripts/check_submission.py   ← 退出码须为0');
console.log('       （原清单引用的 check-ai-patterns.js 从不存在，故该项历批被跳过；');
console.log('        圣上查问时实查，漏掉卷六「第一个部门」等两处序数词。见 lessons R31）');
  console.log('chapters:', chapters.length, 'totalChars:', totalChars, `(${wanZi}万字)`);
});
