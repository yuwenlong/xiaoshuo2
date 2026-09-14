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
const OUT = 'C:/Users/yuwen/Desktop/《重生2011：我把未来写进代码》投稿材料（大纲+正文1-10章）.docx';

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
  '2026年4月15日，37岁的程序员陈序被AI裁员。房贷还剩89.4万，存款11.2万，十五年代码，换来一个纸箱。',
  '再睁眼，2011年7月17日，入职报到前夜。',
  '比特币14美元一个，智能机刚刚起量，公众号还要两年才出生。那场叫“人工智能”的洪水，此刻还只是学术论文里的名词。',
  '他在黑皮笔记本上写下第一行：7月18日，词峰会崩。',
  '这一次，他不当耗材。未来十五年，他要一笔一笔，写进自己的代码里。',
];

const synopsis = [
  '2026年4月15日，37岁的程序员陈序被AI裁员。他负责的业务线，“模型成本是你的十分之一”。房贷剩89.4万，存款11.2万，十五年代码换来一个纸箱。宿醉醒来，他回到2011年7月17日，入职报到前夜：兜里三千块，脑子里装着未来十五年。',
  '没有系统，没有异能，他只有一本黑皮笔记本和一身真本事。从一场全网白屏事故单骑救场开始，他技术立身、步步抢占风口：抄底比特币，公众号上线当天注册，股灾前十天清仓，押注移动互联网与AI浪潮……资产从三千元逐级跃迁，身份从码农到骨干、号主、创业者、投资人。前世抢他功劳的上司、看不懂他却信他的师父、凡事追问“逻辑链”的产品经理林见夏、把裁员名单递到他面前的零界创始人，故人一一走上前来，恩怨都要重算。',
  '但记忆会折旧，风口会改道。当“知道答案”的红利吃到尽头，他必须回答前世没答好的那道题：一个知道答案的人，能不能把日子过成自己想要的样子。2026年4月15日终将再临，这一次，他要坐到桌子的另一边，说出四个字：不裁一人。',
];

const volumes = [
  ['卷一《重回2011》（2011–2012）｜技术立身与原始积累',
    '被AI裁员的陈序重回2011年报到前夜。一场“白屏”事故，他单骑通宵修复，一战立身；面对抢功成性的上司，他隐忍布局，借比特币完成原始积累，在事业部裁撤之日当众反杀。年末，他带着这笔本钱转赴新战场，写下公众号的头一行规划。看点：死局重生、一夜救火、抄底比特币、裁撤日反杀。'],
  ['卷二《风口》（2013–2014）｜公众号矩阵与逃顶',
    '公众号上线当天注册，他与死党袁野组起内容矩阵，粉丝破百万；比特币一路冲高，他在众人不解中精准逃顶、京城置业。监管风波一夜袭来，记忆失灵头一回找上门：前世记得的日子，这一世变了。年末，林见夏回国，事业与感情同时翻页。看点：百万粉矩阵、高位逃顶、监管夜惊魂、嘲笑截图封神。'],
  ['卷三《万众创业》（2014–2016）｜辞职创业与股灾封神',
    '三人小队辞职出海，工具产品用户破千万、月流水破千万；巨头抄袭压顶，团队死战突围。2015年A股疯牛，所有人笑他踏空，他在崩盘前十天清仓离场；十天后5178点雪崩，全场沉默，战投入局。看点：出海战役、巨头抄袭战、股灾前十天清仓。'],
  ['卷四《庄家》（2016–2018）｜从创业者到投资人',
    '转型天使投资人，他布局电商、短视频、新能源多个赛道，并投下零界科技，前世把他送上裁员名单的那家公司。与沧澜资本陆见深正面交锋；2017年末比特币两万美元历史大顶，他再次精准离场，而截胡他的陆见深爆仓出局。看点：被投企业群像、资本博弈、两万美元逃顶、宿敌对比杀。'],
  ['卷五《黑天鹅与AI》（2019–2023）｜穿越黑天鹅，押注AI黎明',
    '疫情黑天鹅，持仓全中；芯片打新、教培双减前清仓，屡次精准避险让“你为什么会知道”的质疑步步收紧。更严峻的是，2022年后他的记忆折旧到只剩方向感，没有答案的陈序，必须证明他依然是他。ChatGPT时刻降临，早年布下的AI仓位浮出水面，“先知”之名出圈。看点：疫情抄底、AI打新、记忆失效危机、ChatGPT时刻。'],
  ['卷六《那个日子》（2024–2026）｜赴约2026.4.15',
    'AI浪潮加冕，资本版图清点；他以大股东身份入主零界，这家公司的裁员名单上，前世有他的名字。2026年4月15日，裁员日重演，董事会要他签字执行“理性方案”，他宣布：不裁一人。IPO钟声里，十五年前那个抱着纸箱走进雨里的下午，终于被翻了过去。看点：零界对决、不裁一人、IPO敲钟、前世今生呼应。'],
];

const persons = [
  ['陈序（男主）', '37岁被AI裁员的资深程序员，重回2011年报到前夜。技术过硬，谋定后动：“我知道成本，所以敢下注”。随身一本黑皮笔记本，记下未来十五年的风口与账目。他的依仗只是记忆，而记忆会折旧、会出错，越往后，越要靠真本事。'],
  ['林见夏（女主）', '产品经理出身，后成为他的COO与合伙人。不懂代码，但懂逻辑、懂人，口头禅“你这个判断，逻辑链呢？”。全书唯一追得上他思维的人，也是唯一最终知晓他秘密的人。感情线克制：从同事到合伙人，先签协议，再谈感情。'],
  ['袁野（联合创始人）', '死党，点火人。大嗓门，屡败屡战，“干就完了”。陈序谋定后动，袁野先干了再说；一个兜底，一个点火。'],
  ['秦深（CTO）', '技术大牛。话不超过十个字，判断从不出错；从不好奇陈序为什么“知道”，不问、不说，只干活。'],
  ['小满（技术骨干）', '实习生出身，陈序带出来的头一个兵。一次误删数据库被他手把手救回，从此“备份”刻进DNA，口头禅是“序哥，我备份过了。”陈序把前世没人教他的，都教给了这个后来者。'],
  ['庞坚（前世宿怨）', '词峰副总监，抢功成性的官僚。不是坏人，是“乌纱优先”的本能：新人太亮，照出他的平庸。两进两出的对手，落魄来投之日，陈序收留了他：“我不是圣人，我是记得被念名字是什么滋味。”'],
  ['陆见深（全书宿敌）', '沧澜资本创始合伙人。模型原教旨主义者，相信一切皆可量化，包括人性。与陈序互为镜像：都信逻辑，一个的逻辑尽头是人，一个的尽头是数。'],
  ['钱总（零界创始人）', '前世把陈序们送上裁员名单的人。他不是恶，是“商业理性”的化身。今生陈序成了他的天使投资人，亦友亦博弈，最终在2026年4月15日迎来正面对决与和解。'],
];

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
    infoRow('书名', '《重生2011：我把未来写进代码》'),
    infoRow('笔名', '沧海横笛'),
    infoRow('题材', '男频·都市·重生·互联网职场＋时代投资（无系统、无异能，重生记忆流）'),
    infoRow('预计篇幅', '500万字以上（六卷＋终章，长篇连载）'),
    infoRow('单章字数', '2000–3000字'),
    infoRow('当前进度', '正文第1–10章已完成，持续稳定更新'),
    infoRow('联系方式', '（投稿前填写：QQ／邮箱／手机）'),
  ],
});

// ---------- 组装 ----------
const children = [];

// 封面
children.push(...spacer(6));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 360 },
  children: [new TextRun({ text: '《重生2011：我把未来写进代码》', font: HEI, size: 52, bold: true })],
}));
children.push(centerP('投稿材料（大纲＋正文第1—10章）', { font: HEI, size: 30, bold: true }));
children.push(...spacer(3));
children.push(centerP('笔名：沧海横笛', { size: 26 }));
children.push(centerP('男频·都市·重生·互联网职场＋时代投资', { size: 22 }));
children.push(...spacer(2));
children.push(centerP('一句话梗概：一个被AI裁掉的37岁程序员，重回2011年报到前夜——这一次，他记得未来十五年每一个风口。', { size: 22 }));
children.push(pageBreak());

// 一、作品信息
children.push(h1('一、作品信息'));
children.push(infoTable);
children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));

// 二、一句话梗概
children.push(h1('二、一句话梗概'));
children.push(bodyP('一个被AI裁掉的37岁程序员，重回2011年报到前夜——这一次，他记得未来十五年每一个风口。'));

// 三、作品简介
children.push(h1('三、作品简介'));
intro.forEach(line => children.push(bodyP(line)));

// 四、故事梗概
children.push(h1('四、故事梗概'));
synopsis.forEach(p => children.push(bodyP(p)));

// 五、分卷大纲
children.push(h1('五、分卷大纲'));
volumes.forEach(([vt, vd]) => {
  children.push(h3(vt));
  children.push(bodyP(vd));
});

// 六、主要人物
children.push(h1('六、主要人物'));
persons.forEach(([name, desc]) => {
  children.push(richP([t(name + '：', { bold: true }), t(desc)]));
});

// 正文收录说明
children.push(h1('七、正文收录说明'));
children.push(bodyP(`以下收录正文第1—10章（第1章至第10章连章原稿，未删节），合计约${wanZi}万字。`));

// 正文
chapters.forEach(ch => {
  children.push(pageBreak());
  children.push(h2(ch.title));
  ch.body.forEach(line => children.push(bodyP(line)));
});

const doc = new Document({
  creator: '沧海横笛',
  title: '《重生2011：我把未来写进代码》投稿材料',
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
  console.log('chapters:', chapters.length, 'totalChars:', totalChars, `(${wanZi}万字)`);
});
